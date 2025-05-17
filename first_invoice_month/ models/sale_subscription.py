from odoo import api, fields, models

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.model
    def create(self, vals):
        # اجعل التاريخ لأول الشهر عند إنشاء الاشتراك
        if vals.get('date_start'):
            try:
                ds = fields.Date.from_string(vals['date_start'])
                vals['date_start'] = fields.Date.to_string(ds.replace(day=1))
            except Exception:
                pass
        if vals.get('next_invoice_date'):
            try:
                nd = fields.Date.from_string(vals['next_invoice_date'])
                vals['next_invoice_date'] = fields.Date.to_string(nd.replace(day=1))
            except Exception:
                pass
        return super().create(vals)

    def write(self, vals):
        if vals.get('date_start'):
            try:
                ds = fields.Date.from_string(vals['date_start'])
                vals['date_start'] = fields.Date.to_string(ds.replace(day=1))
            except Exception:
                pass
        if vals.get('next_invoice_date'):
            try:
                nd = fields.Date.from_string(vals['next_invoice_date'])
                vals['next_invoice_date'] = fields.Date.to_string(nd.replace(day=1))
            except Exception:
                pass
        return super().write(vals)
