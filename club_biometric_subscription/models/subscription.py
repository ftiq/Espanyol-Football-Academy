from odoo import models, fields, api

class ClubSubscription(models.Model):
    _name = 'club.subscription'
    _description = 'Club Subscription Management'

    partner_id = fields.Many2one('res.partner', string='Member', required=True)
    biometric_id = fields.Char(related='partner_id.biometric_id', string='Biometric ID', readonly=True)
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.today)
    end_date = fields.Date(string='End Date', required=True)
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        subscription = super(ClubSubscription, self).create(vals)
        subscription.partner_id.write({
            'subscription_active': True,
            'subscription_end_date': subscription.end_date
        })
        return subscription

    def write(self, vals):
        res = super(ClubSubscription, self).write(vals)
        if 'end_date' in vals or 'active' in vals:
            for sub in self:
                sub.partner_id.write({
                    'subscription_active': sub.active and sub.end_date >= fields.Date.today(),
                    'subscription_end_date': sub.end_date
                })
        return res

    def unlink(self):
        partners = self.mapped('partner_id')
        res = super(ClubSubscription, self).unlink()
        partners.write({
            'subscription_active': False,
            'subscription_end_date': False
        })
        return res

    @api.model
    def cron_check_subscriptions(self):
        today = fields.Date.today()
        expired_subs = self.search([
            ('end_date', '<', today),
            ('active', '=', True)
        ])
        expired_subs.write({'active': False})
        biometric_model = self.env['biometric.device.details']
        for partner in expired_subs.mapped('partner_id'):
            partner.write({'subscription_active': False})
            biometric_model.sync_biometric_status(partner)
