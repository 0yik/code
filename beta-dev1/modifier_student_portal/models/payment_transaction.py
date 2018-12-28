# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
	_inherit = 'payment.transaction'

	invoice_id = fields.Many2one('account.invoice')

	@api.multi
	def write(self, vals):
		if vals.get('state',False) and (self.invoice_id or vals.get('invoice_id',False)):
			if vals.get('state') == 'done':
				invoice_id = False
				payment = False
				invoice_id = self.env['account.invoice'].sudo().browse(self.invoice_id.id or vals.get('invoice_id',False))
				if invoice_id:
					payment_type = invoice_id.type in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
					communication = self.type in ('in_invoice', 'in_refund') and invoice_id.reference or invoice_id.number
					pay_journal = self.env['account.journal'].sudo().search([('type', '=', 'cash')], limit=1)
					payment_method = self.env.ref('account.account_payment_method_manual_in')
					payment = self.env['account.payment'].create({
			            'invoice_ids': [(6, 0, invoice_id and invoice_id.ids or [])],
			            'amount': invoice_id.residual or 0.0,
			            'payment_date': fields.Date.context_today(self),
			            'communication': communication,
			            'partner_id': invoice_id.partner_id.id,
			            'partner_type': invoice_id.type in ('out_invoice', 'out_refund') and 'customer' or 'supplier',
			            'journal_id': pay_journal and pay_journal.id or False,
			            'payment_type': payment_type,
			            'payment_method_id': payment_method.id,
		        	})
		        	if payment:
		        		payment.post()
		res = super(PaymentTransaction, self).write(vals)
		return res