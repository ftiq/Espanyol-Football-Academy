from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('is_subscription', 'date_order', 'subscription_id', 'subscription_state')
    def _compute_start_date(self):
        # هذه الدالة الأصلية قد تحتوي منطق حساب متقدم، لذلك نحتاج لإعادة نفس المنطق أو جزء منه
        for order in self:
            # إذا لم يكن اشتراك أو ليس هناك تاريخ، خليها فارغة
            if not order.is_subscription:
                order.start_date = False
            elif order.subscription_id and order.subscription_id.start_date:
                # نفس منطق أودو: لو اشتراك مجدد، خذ بداية أول اشتراك
                order.start_date = order.subscription_id.start_date
            else:
                # إذا لم يوجد، خذ تاريخ الطلب أو اليوم، وعدله لأول الشهر
                base_date = order.date_order or fields.Date.today()
                if isinstance(base_date, str):
                    base_date = fields.Date.from_string(base_date)
                # غيّر اليوم إلى 1 (أول الشهر)
                order.start_date = base_date.replace(day=1)
