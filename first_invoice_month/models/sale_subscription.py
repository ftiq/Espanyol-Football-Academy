from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('date_order')
    def _compute_start_date(self):
        for order in self:
            if order.date_order:
                # حول date_order لأول يوم في الشهر
                try:
                    d = fields.Date.from_string(order.date_order)
                    order.start_date = d.replace(day=1)
                except Exception:
                    order.start_date = order.date_order
            else:
                # إذا لم يوجد تاريخ طلب، أول يوم من الشهر الحالي
                today = fields.Date.today()
                order.start_date = today.replace(day=1)
