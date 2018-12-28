# -*- coding: utf-8 -*-

import base64
from ast import literal_eval
from odoo import models, fields, api
from odoo.tools import pickle as cPickle


class PosOrder(models.Model):
    _inherit = "pos.order"
    
    @api.model
    def create_from_ui(self, orders):
        # Keep only new orders
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>self, orders ",self, orders
        res = super(PosOrder, self).create_from_ui(orders)
        print "_____________order.get('data').get('amount_paid') ",res, orders[0].get('data').get('amount_paid');
        if res and len(res) >= 1 and orders and orders[0].get('data') and orders[0].get('data').get('amount_paid'):
            pos_order_id = self.env['pos.order'].search([('id', '=', res[0])])
            if pos_order_id and pos_order_id.invoice_id:
                reg_payment_obj = self.env['account.payment']
                reg_payment_data = reg_payment_obj.with_context(default_invoice_ids=[(4, pos_order_id.invoice_id.id, None)]).default_get(['communication', 'currency_id', 'invoice_ids', 'payment_difference', 'partner_id', 'payment_method_id', 'payment_difference_handling', 'journal_id', 'state', 'writeoff_account_id', 'payment_date', 'partner_type', 'payment_token_id', 'hide_payment_method', 'payment_method_code', 'amount', 'payment_type'])
                pay_journal = self.env['account.journal'].sudo().search([('type', '=', 'cash')], limit=1)
                reg_payment_data.update({'journal_id': pay_journal.id,
                    'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                    })
                reg_payment_id = reg_payment_obj.sudo().with_context(active_model='account.invoice',active_ids=pos_order_id.invoice_id.id).create(reg_payment_data)
                payment_data = reg_payment_id.post()
        return res