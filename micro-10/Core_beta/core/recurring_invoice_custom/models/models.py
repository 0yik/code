# -*- coding: utf-8 -*-

from odoo import models, fields, api

class recurring_invoice_custom(models.Model):
	_inherit = 'recurring.invoice'

	@api.onchange('partner_id')
	def get_account_details(self):
		if self.partner_id.customer:
			self.account_id = self.partner_id.property_account_receivable_id
		if self.partner_id.supplier:
			self.account_id = self.partner_id.property_account_payable_id

	@api.multi
	def action_view_customer_invoice(self):
		invoices = []
		for rec in self:
			for line in rec.recurring_schedule_lines:
				if line.invoice_id:
					invoices.append(line.mapped('invoice_id').id)
		action = self.env.ref('account.action_invoice_tree1').read()[0]
		if len(invoices) > 1:
			action['domain'] = [('id', 'in', invoices)]
		elif len(invoices) == 1:
			action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
			action['res_id'] = invoices[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action


class recurring_invoice_line_custom(models.Model):
	_inherit = 'recurring.invoice.line'

	@api.multi
	@api.onchange('product_id')
	def get_product_details(self):
		product = self.product_id.with_context(
			lang=self.partner_id.lang,
			partner=self.partner_id.id
		)
		if self.recurring_invoice_id.partner_id.customer:
			self.name = product.name
			if product.description_sale:
				self.name += '\n' + product.description_sale
			self.account_id = product.property_account_income_id
			self.invoice_line_tax_ids = [(6,0,product.taxes_id.ids)]

		if self.recurring_invoice_id.partner_id.supplier:
			self.name = product.name
			if product.description_purchase:
				self.name += '\n' + product.description_purchase
			self.account_id = product.property_account_expense_id
			self.invoice_line_tax_ids = [(6,0,product.supplier_taxes_id.ids)]
