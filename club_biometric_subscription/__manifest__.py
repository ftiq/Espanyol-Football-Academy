{
    'name': 'Club Biometric Subscription System',
    'version': '18.0.1.0.0',
    'category': 'Membership',
    'summary': "Biometric access control with subscription management",
    'description': """
        This module integrates biometric devices with club subscription system.
        Members can access using their biometric ID when subscription is active.
    """,
    'depends': ['base', 'hr_zk_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_biometric_views.xml',
        'views/subscription_views.xml',
        'views/biometric_device_details_views.xml',
        'data/cron_data.xml',
    ],
    'installable': True,
    'application': True,
}
