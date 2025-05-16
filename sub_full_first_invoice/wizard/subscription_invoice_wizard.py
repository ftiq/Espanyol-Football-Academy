# my_addons/sub_full_first_invoice/wizard/subscription_invoice_wizard.py
from odoo import api, models

class SaleSubscriptionInvoiceWizard(models.TransientModel):
    _inherit = 'sale.subscription.invoice'  # هذا هو اسم الـ wizard في Odoo

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # نحصل على الاشتراك الحالي من context
        sub = self.env['sale.subscription'].browse(self._context.get('active_id'))
        # إذا كان لدينا تاريخ بداية اشتراك
        ds = sub.date_start  # 'YYYY-MM-DD'
        if ds:
            # أول يوم من شهر البداية
            first = ds[:7] + '-01'
            # نوازن الحقلين في الـ wizard
            res['date'] = first                     # تاريخ إنشاء الفاتورة
            res['next_invoice_date'] = first        # لو كنت تريد أيضاً إعادة ضبطه
            # نعيد توليد الفترة من بداية الاشتراك
            start, stop = sub._get_next_period(sub._last_invoice_date)
            # يُمكنك ضبط حقل date_range إن كان ظاهر في الـ wizard
            res['date_range'] = (start, stop)
        return res
