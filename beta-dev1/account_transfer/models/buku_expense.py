# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError

class AccountTransfer(models.Model):
	_name = 'account.transfer'
	_rec_name = 'reference'

	@api.onchange('buku_expense_line_ids')
	def onchange_amount_calculation(self):
		total_amount = 0.0
		for line in self.buku_expense_line_ids:
			total_amount += line.amount_currency
		self.amount = total_amount

	type       = fields.Selection([('in','Transfer In'),('out','Transfer Out')], string='Type')
	journal_id = fields.Many2one('account.journal', string='Journal')
	date       = fields.Date(string='Date')
	reference  = fields.Char(string='Reference')
	account_id = fields.Many2one('account.account', string='Account')
	amount     = fields.Float(string='Amount')
	state = fields.Selection([
		('unposted', 'Unposted'),
		('posted', 'Posted')
	], string='Status', default='unposted', copy=False, index=True, readonly=True, help="Status of the Bank Statement.")
	buku_expense_line_ids = fields.One2many('account.transfer.line','buku_expense_id',string='Bank')

	@api.model
	def create(self,vals):
		total = 0
		if 'buku_expense_line_ids' in vals:
			for line in vals['buku_expense_line_ids']:
				total += line[2]['amount_currency']
			if float_compare(total, vals['amount'], 2) == 1:
				raise UserError(
					_('Total of all Amount Currency cannot be more than Amount.'))

		res = super(AccountTransfer, self).create(vals)
		return res

	@api.multi
	def write(self,vals):
		total = 0
		res = super(AccountTransfer, self).write(vals)
		for line in self.buku_expense_line_ids:
			total += line.amount_currency
		if float_compare(total, self.amount, 2) == 1:
			raise UserError(
				_('Total of all Amount Currency cannot be more than Amount.'))

		return res

	@api.multi
	def action_post(self):
		line_list = []
		for record in self:
			if record.type == 'out':
				credit_line_vals = {
					'name': record.reference,
					'debit': 0.0,
					'credit': record.amount,
					'account_id': record.account_id.id
				}
				line_list.append((0, 0, credit_line_vals))
				for line in record.buku_expense_line_ids:
					debit_line_vals = {
						'name': record.reference,
						'debit': line.amount_currency,
						'credit': 0.0,
						'account_id': line.c_account.id,
					}
					line_list.append((0, 0, debit_line_vals))
			else:
				debit_line_vals = {
					'name': record.reference,
					'debit': record.amount,
					'credit': 0.0,
					'account_id': record.account_id.id
				}
				line_list.append((0, 0, debit_line_vals))
				for line in record.buku_expense_line_ids:
					credit_line_vals = {
						'name': record.reference,
						'debit': 0.0,
						'credit': line.amount_currency,
						'account_id': line.c_account.id,
					}
					line_list.append((0, 0, credit_line_vals))
			move = self.env['account.move'].create({
				'name': '/',
				'journal_id': record.journal_id.id,
				'date': record.date or fields.Date.today(),
				'line_ids': line_list,
				'ref': record.reference
			})
			# move.post()
			self.write({'state': 'posted'})
		return True


class AccountTransferLine(models.Model):
	_name = 'account.transfer.line'

	amount_currency     = fields.Float(string='Amount Currency')
	buku_expense_id = fields.Many2one('account.transfer', string='Bank Transaction')
	c_account = fields.Many2one('account.account', string="Account")
	c_description = fields.Text('Description')

