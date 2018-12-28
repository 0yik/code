# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pos_order(models.Model):
	_inherit = 'pos.order'


	@api.model
	def _process_order(self, order):
		if order.get('payment_debit'):
			if order.get('statement_ids'):
				index = 0
				for statement in order.get('statement_ids'):
					if statement[2].get('amount') == order.get('payment_debit'):
						vals = order.get('statement_ids')
						vals[index][2]['account_id'] = False
						vals[index][2]['statement_id'] = self.env.ref('tm_pos_sales_credit.account_bank_statement_temp').id
						vals[index][2]['journal_id'] = self.env.ref('tm_pos_sales_credit.account_journal_payment_debit').id
						order['statement_ids'] = vals
						break
					index +=1

		res = super(pos_order, self)._process_order(order)

		partner_id = order.get('partner_id')
		payment_debit = order.get('payment_debit')
		if partner_id and payment_debit:
			partner = self.env['res.partner'].browse(partner_id)
			journal = self.env['account.journal'].search([('name', '=', 'Cash')], limit=1)
			payment_methods = journal.outbound_payment_method_ids
			payment_method_id = payment_methods and payment_methods[0] or False
			vals = {
				'payment_type': 'outbound',
				'partner_type': 'customer',
				'partner_id': partner_id,
				'journal_id': journal.id,
				'branch_id': res.branch_id.id,
				'amount' : payment_debit,
				'communication' : 'POS Ref: ' + res.name,
				'payment_method_id': payment_method_id.id

			}
			payment = self.env['account.payment'].create(vals)
			payment.post()
		return res