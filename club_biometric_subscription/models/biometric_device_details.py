from odoo import models, api, _
from odoo.exceptions import UserError
import logging
import pytz
from zk import ZK, const

_logger = logging.getLogger(__name__)

class BiometricDeviceDetails(models.Model):
    _inherit = 'biometric.device.details'

    def sync_biometric_status(self, partner):
        if not partner.biometric_id:
            return
        zk = ZK(self.device_ip, port=self.port_number, timeout=15,
                password=0, force_udp=False, ommit_ping=False)
        conn = self.device_connect(zk)
        if not conn:
            _logger.error("Failed to connect to biometric device for sync")
            return
        try:
            conn.disable_device()
            users = conn.get_users()
            user = next((u for u in users if u.user_id == partner.biometric_id), None)
            if user:
                user.privilege = const.USER_DEFAULT if partner.subscription_active else const.USER_DISABLED
                conn.set_user(uid=partner.biometric_id, privilege=user.privilege)
                _logger.info(f"Updated biometric status for {partner.name} (ID: {partner.biometric_id}) to {user.privilege}")
            else:
                _logger.warning(f"Biometric user not found for {partner.name} (ID: {partner.biometric_id})")
        except Exception as e:
            _logger.error(f"Error syncing biometric status: {str(e)}")
        finally:
            conn.enable_device()
            conn.disconnect()

    def action_download_attendance(self):
        _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        for info in self:
            zk = ZK(info.device_ip, port=info.port_number, timeout=15,
                    password=0, force_udp=False, ommit_ping=False)
            conn = self.device_connect(zk)
            if not conn:
                raise UserError(_('Unable to connect to Biometric Device.'))
            try:
                self.action_set_timezone()
                conn.disable_device()
                users = conn.get_users()
                logs = conn.get_attendance()
                if not logs:
                    _logger.info("No attendance records found.")
                    continue
                for entry in logs:
                    ts = entry.timestamp
                    user_tz = self.env.user.partner_id.tz or 'UTC'
                    local_dt = pytz.timezone(user_tz).localize(ts, is_dst=None)
                    utc_dt = local_dt.astimezone(pytz.utc)
                    punch_str = fields.Datetime.to_string(utc_dt)
                    partner = self.env['res.partner'].search(
                        [('biometric_id', '=', entry.user_id)], limit=1)
                    if not partner:
                        _logger.warning(f"No partner found with biometric ID {entry.user_id}")
                        continue
                    if not partner.check_subscription():
                        _logger.warning(f"Member {partner.name} tried to access with expired subscription")
                        continue
                    if not zk_attendance.search([
                            ('biometric_id', '=', entry.user_id),
                            ('punching_time', '=', punch_str)], limit=1):
                        zk_attendance.create({
                            'partner_id': partner.id,
                            'biometric_id': entry.user_id,
                            'attendance_type': str(entry.status),
                            'punch_type': str(entry.punch),
                            'punching_time': punch_str,
                        })
            except Exception as e:
                _logger.error(f"Error in attendance download: {str(e)}")
            finally:
                conn.enable_device()
                conn.disconnect()
        return True
