from odoo import models, fields

class ZKMachineAttendance(models.Model):
    _name = 'zk.machine.attendance'
    _description = 'Biometric Attendance Log'

    partner_id = fields.Many2one('res.partner', string='Member')
    biometric_id = fields.Char(string='Biometric ID')
    attendance_type = fields.Char(string='Status')
    punch_type = fields.Char(string='Punch')
    punching_time = fields.Datetime(string='Timestamp')
