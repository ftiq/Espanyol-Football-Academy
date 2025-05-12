# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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

# Import ZK from either zk or pyzk package
try:
    from zk import ZK, const
except ImportError:
    try:
        from pyzk.zk import ZK, const
    except ImportError:
        _logger.error("Pyzk library not found. Please install with 'pip3 install pyzk'.")
        ZK = None
        const = None

class BiometricDeviceDetails(models.Model):
    """Model for configuring and connecting the biometric device with Odoo"""
    _name = 'biometric.device.details'
    _description = 'Biometric Device Details'

    name = fields.Char(string='Name', required=True, help='Record Name')
    device_ip = fields.Char(string='Device IP', required=True,
                            help='The IP address of the Device')
    port_number = fields.Integer(string='Port Number', required=True,
                                 help="The Port Number of the Device")
    address_id = fields.Many2one('res.partner', string='Working Address',
                                 help='Working address of the partner')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id.id,
                                 help='Current Company')
    device_password = fields.Char(string='Device Password', default='0', help='Password for ZK device')

    def _get_zk_connection(self):
        """Helper to instantiate ZK and connect"""
        if not ZK:
            raise UserError(_("Pyzk module not found. Please install with 'pip3 install pyzk'."))
        zk = ZK(self.device_ip, port=self.port_number, timeout=30,
                password=int(self.device_password or 0),
                force_udp=False, ommit_ping=False)
        conn = zk.connect()
        return conn

    def action_test_connection(self):
        """Checking the connection status"""
        try:
            conn = self._get_zk_connection()
            conn.disconnect()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Successfully Connected',
                    'type': 'success',
                    'sticky': False
                }
            }
        except Exception as error:
            raise ValidationError(_(str(error)))

    def action_set_timezone(self):
        """Set device time to user's timezone"""
        for record in self:
            try:
                conn = record._get_zk_connection()
                user_tz = self.env.context.get('tz') or self.env.user.tz or 'UTC'
                now_utc = pytz.utc.localize(fields.Datetime.now())
                local_time = now_utc.astimezone(pytz.timezone(user_tz))
                conn.set_time(local_time)
                conn.disconnect()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Successfully Set the Time',
                        'type': 'success',
                        'sticky': False
                    }
                }
            except Exception as error:
                raise UserError(_(str(error)))

    def action_clear_attendance(self):
        """Clear attendance records on device and in log"""
        for record in self:
            try:
                conn = record._get_zk_connection()
                conn.enable_device()
                data = conn.get_attendance()
                if data:
                    conn.clear_attendance()
                    self._cr.execute("DELETE FROM zk_machine_attendance")
                    conn.disconnect()
                else:
                    raise UserError(_(
                        'Attendance log is empty or cannot be retrieved.'
                    ))
            except Exception as error:
                raise UserError(_(str(error)))

    @api.model
    def cron_download(self):
        machines = self.search([])
        for machine in machines:
            machine.action_download_attendance()

    def action_download_attendance(self):
        """Download attendance records from device and create logs"""
        zk_attendance = self.env['zk.machine.attendance']
        hr_attendance = self.env['hr.attendance']
        for record in self:
            conn = record._get_zk_connection()
            record.action_set_timezone()
            conn.disable_device()
            users = conn.get_users()
            attendance = conn.get_attendance()
            if not attendance:
                conn.disconnect()
                raise UserError(_('No attendance records found.'))
            for each in attendance:
                punch_time = each.timestamp
                local_tz = pytz.timezone(self.env.user.partner_id.tz or 'UTC')
                local_dt = local_tz.localize(punch_time, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                punch_str = fields.Datetime.to_string(utc_dt)
                employee = self.env['hr.employee'].search([
                    ('device_id_num', '=', each.user_id)], limit=1)
                if not employee:
                    user_info = next((u for u in users if u.user_id == each.user_id), None)
                    employee = self.env['hr.employee'].create({
                        'device_id_num': each.user_id,
                        'name': user_info.name if user_info else _('Unknown')
                    })
                if not zk_attendance.search([
                        ('device_id_num', '=', each.user_id),
                        ('punching_time', '=', punch_str)
                ], limit=1):
                    zk_attendance.create({
                        'employee_id': employee.id,
                        'device_id_num': each.user_id,
                        'attendance_type': str(each.status),
                        'punch_type': str(each.punch),
                        'punching_time': punch_str,
                        'address_id': record.address_id.id
                    })
                open_att = hr_attendance.search([
                    ('employee_id', '=', employee.id),
                    ('check_out', '=', False)
                ], limit=1)
                if each.punch == const.CHECK_IN:
                    if not open_att:
                        hr_attendance.create({
                            'employee_id': employee.id,
                            'check_in': punch_str
                        })
                elif each.punch == const.CHECK_OUT:
                    if open_att:
                        open_att.write({'check_out': punch_str})
                    else:
                        last_att = hr_attendance.search([
                            ('employee_id', '=', employee.id)
                        ], order='check_in desc', limit=1)
                        if last_att:
                            last_att.write({'check_out': punch_str})
            conn.disconnect()
            return True

    def action_restart_device(self):
        """Restart the biometric device"""
        conn = self._get_zk_connection()
        conn.restart()
        conn.disconnect()
