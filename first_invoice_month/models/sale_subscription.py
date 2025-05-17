from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        # اضبط تاريخ أول فاتورة على بداية الشهر
        if vals.get('next_invoice_date'):
            try:
                nd = fields.Date.from_string(vals['next_invoice_date'])
                vals['next_invoice_date'] = nd.replace(day=1)
            except Exception:
                pass
        order = super().create(vals)
        return order

    def write(self, vals):
        res = super().write(vals)
        for order in self:
            if order.next_invoice_date:
                try:
                    nd = fields.Date.from_string(order.next_invoice_date)
                    order.next_invoice_date = nd.replace(day=1)
                except Exception:
                    pass
        return res
