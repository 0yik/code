# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartnerBank(models.Model):

	_inherit = "res.partner.bank"

	branch_code = fields.Char('Branch Code')
	swift_code = fields.Char('SWIFT Code')
	remarks = fields.Text('Remarks')

class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	cust_sup_bank_account_id = fields.Many2one('res.partner.bank', string="Bank Account")
