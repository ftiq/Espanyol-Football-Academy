# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.model
    def create(self, vals):
        # تأكد أن date_start و next_invoice_date في أول الشهر
        if vals.get('date_start'):
            try:
                ds = fields.Date.from_string(vals['date_start'])
                vals['date_start'] = ds.replace(day=1)
            except Exception:
                pass
        if vals.get('next_invoice_date'):
            try:
                nd = fields.Date.from_string(vals['next_invoice_date'])
                vals['next_invoice_date'] = nd.replace(day=1)
            except Exception:
                pass
        return super().create(vals)

    def write(self, vals):
        # تأكد أن date_start و next_invoice_date في أول الشهر
        if vals.get('date_start'):
            try:
                ds = fields.Date.from_string(vals['date_start'])
                vals['date_start'] = ds.replace(day=1)
            except Exception:
                pass
        if vals.get('next_invoice_date'):
            try:
                nd = fields.Date.from_string(vals['next_invoice_date'])
                vals['next_invoice_date'] = nd.replace(day=1)
            except Exception:
                pass
        return super().write(vals)
