# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.model
    def _get_next_recurring_date(self, last_date, interval_type, interval_number):
        # لو تريد أن تحسب من تاريخ بداية الاشتراك وليس من نهاية الشهر
        # last_date: هو تاريخ آخر فاتورة
        # نعيد التاريخ بزيادة شهر كامل من آخر تاريخ فاتورة
        if interval_type == 'monthly':
            return last_date + relativedelta(months=interval_number)
        elif interval_type == 'yearly':
            return last_date + relativedelta(years=interval_number)
        # بقية الأنواع نفس الكود الافتراضي
        return super()._get_next_recurring_date(last_date, interval_type, interval_number)
