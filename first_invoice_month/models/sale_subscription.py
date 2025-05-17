from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('date_order', 'plan_id')  # ضع هنا أي حقل يؤثر فعلاً على start_date
    def _compute_start_date(self):
        for order in self:
            # مثال: دائماً أول الشهر من تاريخ الطلب
            if order.is_subscription:
                if order.date_order:
                    # حوّل date_order إلى أول الشهر
                    try:
                        d = fields.Date.from_string(order.date_order)
                        order.start_date = d.replace(day=1)
                    except Exception:
                        order.start_date = order.date_order
                else:
                    order.start_date = fields.Date.today().replace(day=1)
            else:
                order.start_date = False
