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
try:
    from pyzk.zk import ZK, const
except ImportError:
    _logger.error("pyzk library not found in module. Ensure 'pyzk/' is vendored alongside.")


class BiometricDeviceDetails(models.Model):
    """Model for configuring and connect the biometric device with odoo"""
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

    def device_connect(self, zk):
        """Function for connecting the device with Odoo"""
        try:
            conn = zk.connect()
            return conn
        except Exception:
            return False

    def action_test_connection(self):
        """Checking the connection status"""
        zk = ZK(self.device_ip, port=self.port_number, timeout=30,
                password=False, ommit_ping=False)
        try:
            conn = zk.connect()
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
            raise ValidationError(f'{error}')

    def action_set_timezone(self):
        """Function to set user's timezone to device"""
        for info in self:
            zk = ZK(info.device_ip, port=info.port_number, timeout=15,
                    password=0, force_udp=False, ommit_ping=False)
            conn = self.device_connect(zk)
            if not conn:
                raise UserError(_("Pyzk module not found."))
            user_tz = self.env.context.get('tz') or self.env.user.tz or 'UTC'
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
                    'sticky': False
                }
            }

    def action_clear_attendance(self):
        """Method to clear record from the zk.machine.attendance model and from the device"""
        for info in self:
            zk = ZK(info.device_ip, port=info.port_number, timeout=30,
                    password=0, force_udp=False, ommit_ping=False)
            conn = self.device_connect(zk)
            if not conn:
                raise UserError(_('Unable to connect to Attendance Device.'))
            conn.enable_device()
            logs = conn.get_attendance()
            if not logs:
                conn.disconnect()
                raise UserError(_('Attendance log is empty.'))
            conn.clear_attendance()
            self._cr.execute("DELETE FROM zk_machine_attendance")
            conn.disconnect()

    @api.model
    def cron_download(self):
        machines = self.search([])
        for machine in machines:
            machine.action_download_attendance()

    def action_download_attendance(self):
        """Function to download attendance records from the device"""
        _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        hr_attendance = self.env['hr.attendance']
        for info in self:
            zk = ZK(info.device_ip, port=info.port_number, timeout=15,
                    password=0, force_udp=False, ommit_ping=False)
            conn = self.device_connect(zk)
            if not conn:
                raise UserError(_('Unable to connect to Attendance Device.'))
            # synchronize device time
            self.action_set_timezone()
            conn.disable_device()
            users = conn.get_users()
            logs = conn.get_attendance()
            if not logs:
                conn.disconnect()
                raise UserError(_('No attendance records found.'))
            for entry in logs:
                ts = entry.timestamp
                user_tz = self.env.user.partner_id.tz or 'UTC'
                local_dt = pytz.timezone(user_tz).localize(ts, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                punch_str = fields.Datetime.to_string(utc_dt)

                emp = self.env['hr.employee'].search(
                    [('device_id_num', '=', entry.user_id)], limit=1)
                if not emp:
                    user_info = next((u for u in users if u.user_id == entry.user_id), None)
                    emp = self.env['hr.employee'].create({
                        'device_id_num': entry.user_id,
                        'name': user_info.name if user_info else _('Unknown')
                    })

                # create zk log if new
                if not zk_attendance.search([
                        ('device_id_num', '=', entry.user_id),
                        ('punching_time', '=', punch_str)], limit=1):
                    zk_attendance.create({
                        'employee_id': emp.id,
                        'device_id_num': entry.user_id,
                        'attendance_type': str(entry.status),
                        'punch_type': str(entry.punch),
                        'punching_time': punch_str,
                    })

                # record hr.attendance
                open_att = hr_attendance.search([
                    ('employee_id', '=', emp.id),
                    ('check_out', '=', False)], limit=1)
                if entry.punch == const.CHECK_IN and not open_att:
                    hr_attendance.create({
                        'employee_id': emp.id,
                        'check_in': punch_str
                    })
                elif entry.punch == const.CHECK_OUT:
                    if open_att:
                        open_att.write({'check_out': punch_str})
                    else:
                        last = hr_attendance.search(
                            [('employee_id', '=', emp.id)],
                            order='check_in desc', limit=1)
                        if last:
                            last.write({'check_out': punch_str})

            conn.disconnect()
        return True

    def action_restart_device(self):
        """For restarting the device"""
        zk = ZK(self.device_ip, port=self.port_number, timeout=15,
                password=0, force_udp=False, ommit_ping=False)
        conn = self.device_connect(zk)
        if not conn:
            raise UserError(_("Unable to connect to device to restart."))
        conn.restart()
        conn.disconnect()
