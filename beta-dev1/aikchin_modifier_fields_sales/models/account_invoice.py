# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	internal_note = fields.Text(string='Internal Note')
	issuer_id = fields.Many2one('hr.employee', 'Issuer')
