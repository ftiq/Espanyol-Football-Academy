from odoo import http
from odoo.http import request

class XtraAPIController(http.Controller):

    @http.route('/api/contacts', type='json', auth='user', methods=['GET'], csrf=False)
    def get_contacts(self):
        contacts = request.env['res.partner'].sudo().search([('customer_rank', '>', 0)])
        return [
            {
                'id': c.id,
                'name': c.name,
                'email': c.email,
                'phone': c.phone,
                'mobile': c.mobile,
                'salesman_id': c.user_id.name if c.user_id else None,
            }
            for c in contacts
        ]

    @http.route('/api/salesmen', type='json', auth='user', methods=['GET'], csrf=False)
    def get_salesmen(self):
        salesmen = request.env['salesman.profile'].sudo().search([])
        return [
            {
                'id': s.id,
                'name': s.name,
                'mobile': s.mobile,
                'warehouse': s.warehouse_id.name if s.warehouse_id else None,
                'customers': [p.name for p in s.customer_ids],
            }
            for s in salesmen
        ]

    @http.route('/api/visits', type='json', auth='user', methods=['GET'], csrf=False)
    def get_visits(self):
        visits = request.env['salesman.visit.log'].sudo().search([])
        return [
            {
                'id': v.id,
                'salesman': v.salesman_id.name if v.salesman_id else None,
                'customer': v.customer_id.name if v.customer_id else None,
                'date': v.date.strftime('%Y-%m-%d %H:%M:%S'),
                'status': v.status,
                'notes': v.notes,
            }
            for v in visits
        ]
