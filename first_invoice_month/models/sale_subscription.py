from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        # عند إنشاء سجل جديد، عدّل التواريخ لأوّل الشهر إن وجدت
        for field_name in ['start_date', 'date_order', 'next_invoice_date']:
            date_val = vals.get(field_name)
            if date_val:
                try:
                    d = fields.Date.from_string(date_val)
                    vals[field_name] = d.replace(day=1)
                except Exception:
                    pass
        return super().create(vals)

    def write(self, vals):
        res = super().write(vals)
        # بعد التعديل، عدّل الحقول الثلاثة لو قيمتها موجودة
        for record in self:
            for field_name in ['start_date', 'date_order', 'next_invoice_date']:
                date_val = getattr(record, field_name, False)
                if date_val:
                    try:
                        d = fields.Date.from_string(date_val)
                        setattr(record, field_name, d.replace(day=1))
                    except Exception:
                        pass
        return res
