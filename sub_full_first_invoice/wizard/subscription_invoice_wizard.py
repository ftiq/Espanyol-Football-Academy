# -*- coding: utf-8 -*-
from odoo import api, models

class SubscriptionInvoiceWizard(models.TransientModel):
    _inherit = 'sale.subscription.invoice'

    @api.model
    def default_get(self, fields_list):
        res = super(SubscriptionInvoiceWizard, self).default_get(fields_list)
        order_id = self._context.get('active_id')
        if order_id:
            sub = self.env['sale.subscription'].search(
                [('order_id', '=', order_id)], limit=1)
            if sub and sub.date_start:
                first = sub.date_start[:7] + '-01'
                res.update({
                    'date': first,
                    'next_invoice_date': first,
                })
        return res
