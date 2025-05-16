from odoo import models, fields, api
from datetime import date

class SubscriptionCustom(models.Model):
    _inherit = 'sale.subscription'
    
    def set_first_day_invoice(self):
        """Set next invoice date to 1st of current month"""
        first_day = date.today().replace(day=1)
        self.write({'next_invoice_date': first_day})
        
    @api.model
    def cron_update_all_subscriptions(self):
        """Scheduled action to update all active subscriptions"""
        subscriptions = self.search([('state', '=', 'open')])
        for sub in subscriptions:
            sub.set_first_day_invoice()
