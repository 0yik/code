# -*- coding: utf-8 -*-
from odoo import api, models, fields, registry
import json
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    event = fields.Char('event')
    event_date = fields.Date(string='Event Date', default=fields.Date.context_today, required=True, copy=False)

    @api.model
    def get_list_customer_deposit(self):
        customers = self.env['account.payment'].search([('is_deposit', '=', True), ('payment_type', '=', 'inbound'),('partner_type', '=', 'customer'),('state','=','posted')], limit=100)
        result = []
        for customer in customers:
            result.append(customer.convert_to_json())
        return result

    @api.model
    def convert_to_json(self):
        return {
            'id': self.id,
            'communication': self.communication,
            'journal_id': self.journal_id,
            'name': self.name,
            'partner_id': self.partner_id.name,
            'payment_date': self.payment_date,
            'amount': self.amount,
            'state': self.state,
        }

    @api.model
    def create_customer_deposit_from_pos(self,data):
        vals = {
            'is_deposit': True,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_method_id': 1,
        }
        data.update(vals)
        result = self.env['account.payment'].create(data)
        result.post()
        return {'code': 200,'payment':result.id}

    @api.model
    def update_amount_payment(self, data):
        for item in data:
            exist_ap = self.browse(item.get('id'))
            if exist_ap:
                exist_ap.remaining_amount -= item.get('amount')
                if exist_ap.remaining_amount == 0:
                    exist_ap.state = 'reconciled'
        return {'code': 200}
