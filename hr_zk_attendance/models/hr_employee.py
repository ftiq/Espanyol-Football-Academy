# -*- coding: utf-8 -*-
from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'
    device_id_num = fields.Char(string='Device ID')
