from odoo import api, fields, models

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.model
    def create(self, vals):
        # اجعل التاريخ لأول الشهر عند إنشاء الاشتراك
        if vals.get('date_start'):
            try:
                ds = fields.Date.from_string(vals['date_start'])
                vals['date_start'] = ds.replace(day=1)
            except Exception:
                pass
        subscription = super().create(vals)
        # عدل next_invoice_date بعد الإنشاء
        if subscription.next_invoice_date:
            try:
                nd = fields.Date.from_string(subscription.next_invoice_date)
                subscription.next_invoice_date = nd.replace(day=1)
            except Exception:
                pass
        return subscription

    def write(self, vals):
        res = super().write(vals)
        for sub in self:
            if sub.date_start:
                try:
                    ds = fields.Date.from_string(sub.date_start)
                    sub.date_start = ds.replace(day=1)
                except Exception:
                    pass
            if sub.next_invoice_date:
                try:
                    nd = fields.Date.from_string(sub.next_invoice_date)
                    sub.next_invoice_date = nd.replace(day=1)
                except Exception:
                    pass
        return res
