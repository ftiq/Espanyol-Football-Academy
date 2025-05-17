from odoo import models, fields, api
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if vals.get('next_invoice_date') and vals.get('date_start'):
            try:
                start_date = fields.Date.from_string(vals['date_start'])
                next_inv = fields.Date.from_string(vals['next_invoice_date'])
                # اجعل تاريخ الفاتورة التالية أول الشهر بعد start_date إذا كانوا متساويين
                if next_inv <= start_date:
                    next_inv = (start_date + timedelta(days=32)).replace(day=1)
                vals['next_invoice_date'] = next_inv
            except Exception:
                pass
        order = super().create(vals)
        return order

    def write(self, vals):
        res = super().write(vals)
        for order in self:
            if order.next_invoice_date and order.date_start:
                try:
                    if order.next_invoice_date <= order.date_start:
                        next_inv = (order.date_start + timedelta(days=32)).replace(day=1)
                        order.next_invoice_date = next_inv
                except Exception:
                    pass
        return res
