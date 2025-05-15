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
from odoo import fields, models

class ZkMachineAttendance(models.Model):
    """Model to hold raw biometric attendance records"""
    _name = 'zk.machine.attendance'
    _description = 'ZK Machine Attendance'
    _order = 'punching_time desc'

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  help='Related Odoo employee')
    device_id_num = fields.Char(string='Biometric Device ID',
                                help='Identifier of the user on the device')
    attendance_type = fields.Selection([
        ('1', 'Finger'), ('15', 'Face'),
        ('2', 'Type_2'), ('3', 'Password'),
        ('4', 'Card'), ('255', 'Duplicate')
    ], string='Category',
    help='Method used to record attendance')
    punch_type = fields.Selection([
        ('0', 'Check In'), ('1', 'Check Out'),
        ('2', 'Break Out'), ('3', 'Break In'),
        ('4', 'Overtime In'), ('5', 'Overtime Out'),
        ('255', 'Duplicate')
    ], string='Punching Type',
    help='Type of punch event')
    punching_time = fields.Datetime(string='Punching Time',
                                   help='Timestamp of the punch')
    address_id = fields.Many2one('res.partner', string='Working Address',
                                 help='Working address of the employee')
