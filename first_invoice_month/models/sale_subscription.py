from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        # عند إنشاء أمر البيع، اجعل التاريخ لأول الشهر
        if vals.get('date_order'):
            try:
                ds = fields.Date.from_string(vals['date_order'])
                vals['date_order'] = ds.replace(day=1)
            except Exception:
                pass
        return super().create(vals)

    def write(self, vals):
        res = super().write(vals)
        for order in self:
            if order.date_order:
                try:
                    ds = fields.Date.from_string(order.date_order)
                    order.date_order = ds.replace(day=1)
                except Exception:
                    pass
        return res
