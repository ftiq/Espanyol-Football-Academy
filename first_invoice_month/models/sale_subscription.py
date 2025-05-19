# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.model
    def _get_next_recurring_date(self, last_date, interval_type, interval_number):
        """Compute the next recurring date based on last_date and interval.
        
        Args:
            last_date (date): The date of the last invoice
            interval_type (str): 'daily', 'weekly', 'monthly', or 'yearly'
            interval_number (int): Number of intervals to add
            
        Returns:
            date: The next recurring date
        """
        if interval_type == 'monthly':
            return last_date + relativedelta(months=interval_number)
        elif interval_type == 'yearly':
            return last_date + relativedelta(years=interval_number)
        # For other interval types, fall back to default implementation
        return super(SaleSubscription, self)._get_next_recurring_date(
            last_date, interval_type, interval_number)
