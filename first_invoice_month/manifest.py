{
    'name': 'First Invoice Month',
    'version': '1.0',
    'summary': 'Set next invoice date to first day of month',
    'description': 'Automatically sets subscription next invoice date to 1st of each month',
    'author': 'Your Name',
    'depends': ['sale_subscription'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
