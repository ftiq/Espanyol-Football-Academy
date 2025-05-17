# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('is_subscription')
    def _compute_start_date(self):
        for so in self:
            if not so.is_subscription:
                so.start_date = False
            elif not so.start_date:
                # يمكنك تغيير السطر التالي لو عندك شرط معين (مثال: اليوم + 7 أيام أو حسب حقل آخر)
                so.start_date = fields.Date.today()
