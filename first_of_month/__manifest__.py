# -*- coding: utf-8 -*-
{
    'name': 'Subscription: Set Dates to First of Month',
    'version': '1.0.0',
    'author': 'Your Company',
    'category': 'Sales',
    'summary': 'Automatically aligns subscription dates to the first day of month.',
    'description': """
        This module sets date_start and next_invoice_date of sale subscriptions
        to the first day of the selected month on create and update.
    """,
    'depends': ['sale_subscription'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
