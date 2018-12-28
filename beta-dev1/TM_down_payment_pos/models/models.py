# -*- coding: utf-8 -*-
from odoo import api, models, fields, registry,_
import json
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
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
            pay_id = self.browse(item.get('id'))
            if pay_id and pay_id.remaining_amount > item.get('amount'):
                account_move_vals = {
                    'journal_id': pay_id.journal_id.id,
                    'date': fields.date.today(),
                    'amount': pay_id.remaining_amount,
                }
                move_id = self.env['account.move'].create(account_move_vals)
                move_line_tml = {
                    'payment_id': pay_id.id,
                    'name': u'Payment Pos Reconcile',
                    'invoice_id': False,
                    'journal_id': pay_id.journal_id.id,
                    'currency_id': False,
                    'amount_currency': False,
                    'partner_id': pay_id.partner_id.commercial_partner_id.id,
                    'move_id': move_id.id
                }
                move_line_tml.update({
                    'credit': 0.0,
                    'debit': item.get('amount'),
                    'account_id': pay_id.writeoff_account_id.id
                })
                move_id1 = self.with_context(check_move_validity=False).env['account.move.line'].create(move_line_tml)
                move_line_tml.update({
                    'credit': item.get('amount'),
                    'debit': 0.0,
                    'account_id': pay_id.writeoff_account_id.id
                })
                move_id2 = self.with_context(check_move_validity=False).env['account.move.line'].create(move_line_tml)
                move_id.post()
                pay_id.remaining_amount -= item.get('amount')
                if pay_id.remaining_amount == 0:
                    pay_id.state = 'reconciled'
        return {'code': 200}

