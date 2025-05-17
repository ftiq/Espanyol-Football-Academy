from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def fix_subscription_dates(self):
        for order in self:
            if order.is_subscription:
                # بداية الفترة أول الشهر الحالي
                today = fields.Date.today()
                start_date = today.replace(day=1)
                order.start_date = start_date
                # الفاتورة القادمة أول الشهر القادم (إذا كانت خطة شهرية)
                if order.plan_id and order.plan_id.billing_period_unit == 'month':
                    next_invoice_date = (start_date + relativedelta(months=1))
                    order.next_invoice_date = next_invoice_date
                # الحالة إلى نشط
                order.subscription_state = '3_progress'
