# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrder, self).default_get(fields_list)
        if 'date_order' in res:
            today = fields.Date.context_today(self)
            first = today[:7] + '-01 00:00:00'
            res['date_order'] = first
        return res

    @api.model
    def create(self, vals):
        if 'date_order' not in vals:
            today = fields.Date.context_today(self)
            first = today[:7] + '-01 00:00:00'
            vals['date_order'] = first
        return super(SaleOrder, self).create(vals)
