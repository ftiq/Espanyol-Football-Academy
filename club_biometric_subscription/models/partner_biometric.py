from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    biometric_id = fields.Char(string='Biometric ID')
    subscription_active = fields.Boolean(string='Active Subscription', default=False)
    subscription_end_date = fields.Date(string='Subscription End Date')

    def check_subscription(self):
        self.ensure_one()
        if self.subscription_end_date:
            return self.subscription_end_date >= fields.Date.today()
        return False

    @api.model
    def update_subscription_status(self):
        partners = self.search([('biometric_id', '!=', False)])
        for partner in partners:
            new_status = partner.check_subscription()
            if partner.subscription_active != new_status:
                partner.subscription_active = new_status
                self.env['biometric.device.details'].sync_biometric_status(partner)
