# -*- coding: utf-8 -*-
{
    'name': 'Order: Set Dates to First of Month',
    'version': '1.0.0',
    'author': 'Your Company',
    'category': 'Sales',
    'summary': 'Automatically aligns sales order dates to the first day of month.',
    'description': """
        This module sets date fields of sales orders to the first day of the selected month on create and update.
    """,
    'depends': ['sale'],  # أو ['sale_management'] إذا كان هو المتوفر عندك
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
