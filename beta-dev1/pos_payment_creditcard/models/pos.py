from odoo import api, fields, models, _
import json
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from functools import partial

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    need_input = fields.Boolean('Need Input')
    max_digits = fields.Integer('Max Digits')
    min_digits = fields.Integer('Min Digits')

class PosOrder(models.Model):
    _inherit = 'pos.order'

    payment_ref = fields.Char('Payment Ref No')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        print "\n\n\n\n\n\n\n\n\n\n",ui_order.get('payment_ref')
        res['payment_ref'] = ui_order.get('payment_ref')
        return res

    def _create_account_move(self, dt, ref, journal_id, company_id):
        move =  super(PosOrder, self)._create_account_move(dt, ref, journal_id, company_id)
        if '-' in ref:
            ref = ref.split('-')[0].strip()
	orders = self.env['pos.order'].search([('session_id.name', '=', ref)])
        if orders and move.journal_id.need_input:
            payment_ref = [order.payment_ref for order in orders if order.payment_ref]
            move.payment_ref = ','.join(payment_ref)
        return move

class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_ref = fields.Char('Payment Ref')
