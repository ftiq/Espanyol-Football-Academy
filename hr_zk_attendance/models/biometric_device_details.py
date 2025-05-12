# -*- coding: utf-8 -*-
# Add vendored pyzk package to Python path
import sys, os

# Ensure 'pyzk' directory under module is discoverable
MODULE_PATH = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(MODULE_PATH, 'pyzk'))

# Now import models
from . import models
# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Bhagyadev KP (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################
import datetime
import logging
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Import ZK and constants from vendored pyzk
from pyzk.zk import ZK, const

class BiometricDeviceDetails(models.Model):
    """Model for configuring and connecting the biometric device with Odoo"""
    _name = 'biometric.device.details'
    _description = 'Biometric Device Details'

    name = fields.Char(string='Name', required=True, help='Record Name')
    device_ip = fields.Char(string='Device IP', required=True,
                            help='The IP address of the Device')
    port_number = fields.Integer(string='Port Number', required=True,
                                 help='The Port Number of the Device')
    address_id = fields.Many2one('res.partner', string='Working Address',
                                 help='Working address of the partner')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id.id,
                                 help='Current Company')

    def _get_connection(self):
        """Helper to connect to the biometric device"""
        zk = ZK(self.device_ip,
                port=self.port_number,
                timeout=30,
                password=0,
                force_udp=False,
                ommit_ping=False)
        try:
            return zk.connect()
        except Exception as err:
            raise UserError(_(str(err)))

    def action_test_connection(self):
        """Test connectivity to the biometric device"""
        conn = self._get_connection()
        conn.disconnect()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Successfully Connected',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_set_timezone(self):
        """Set device time to current user's timezone"""
        for rec in self:
            conn = rec._get_connection()
            user_tz = (self.env.context.get('tz') or self.env.user.tz or 'UTC')
            now_utc = pytz.utc.localize(fields.Datetime.now())
            local_dt = now_utc.astimezone(pytz.timezone(user_tz))
            conn.set_time(local_dt)
            conn.disconnect()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Successfully Set the Time',
                    'type': 'success',
                    'sticky': False,
                }
            }

    def action_clear_attendance(self):
        """Clear all attendance logs on the device and locally"""
        for rec in self:
            conn = rec._get_connection()
            conn.enable_device()
            logs = conn.get_attendance()
            if not logs:
                conn.disconnect()
                raise UserError(_('Attendance log is empty.'))
            conn.clear_attendance()
            self._cr.execute('DELETE FROM zk_machine_attendance')
            conn.disconnect()

    @api.model
    def cron_download(self):
        """Scheduled job: download attendance from all configured devices"""
        for device in self.search([]):
            device.action_download_attendance()

    def action_download_attendance(self):
        """Download and import attendance records into Odoo"""
        zk_logs = self.env['zk.machine.attendance']
        hr_logs = self.env['hr.attendance']
        for rec in self:
            conn = rec._get_connection()
            rec.action_set_timezone()
            conn.disable_device()
            users = conn.get_users()
            logs = conn.get_attendance()
            if not logs:
                conn.disconnect()
                raise UserError(_('No attendance records found.'))
            for entry in logs:
                punch_time = entry.timestamp
                user_tz = self.env.user.partner_id.tz or 'UTC'
                local_dt = pytz.timezone(user_tz).localize(punch_time, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                punch_str = fields.Datetime.to_string(utc_dt)
                # Find or create employee by device_id_num
                emp = self.env['hr.employee'].search([
                    ('device_id_num', '=', entry.user_id)], limit=1
                )
                if not emp:
                    user_info = next((u for u in users if u.user_id == entry.user_id), None)
                    emp = self.env['hr.employee'].create({
                        'device_id_num': entry.user_id,
                        'name': user_info.name if user_info else _('Unknown')
                    })
                # Prevent duplicates
                if not zk_logs.search([
                        ('device_id_num', '=', entry.user_id),
                        ('punching_time', '=', punch_str)
                    ], limit=1):
                    zk_logs.create({
                        'employee_id': emp.id,
                        'device_id_num': entry.user_id,
                        'attendance_type': str(entry.status),
                        'punch_type': str(entry.punch),
                        'punching_time': punch_str,
                        'address_id': rec.address_id.id,
                    })
                # Handle HR attendance record
                open_log = hr_logs.search([
                    ('employee_id', '=', emp.id),
                    ('check_out', '=', False)
                ], limit=1)
                if entry.punch == const.CHECK_IN and not open_log:
                    hr_logs.create({'employee_id': emp.id, 'check_in': punch_str})
                elif entry.punch == const.CHECK_OUT:
                    if open_log:
                        open_log.write({'check_out': punch_str})
                    else:
                        last_att = hr_logs.search([
                            ('employee_id', '=', emp.id)
                        ], order='check_in desc', limit=1)
                        if last_att:
                            last_att.write({'check_out': punch_str})
            conn.disconnect()
        return True

    def action_restart_device(self):
        """Restart the biometric device remotely"""
        conn = self._get_connection()
        conn.restart()
        conn.disconnect()
