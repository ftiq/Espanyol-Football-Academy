# -*- coding: utf-8 -*-
from odoo import models, fields

class ZKMachineAttendance(models.Model):
    _name = 'zk.machine.attendance'
    employee_id = fields.Many2one('hr.employee', string='Employee')
    device_id_num = fields.Char(string='Device ID')
    attendance_type = fields.Char(string='Status')
    punch_type = fields.Char(string='Punch')
    punching_time = fields.Datetime(string='Timestamp')
