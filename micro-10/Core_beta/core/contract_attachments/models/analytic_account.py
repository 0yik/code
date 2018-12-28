# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountAnalyticAttachment(models.Model):
    _name = 'account.analytic.attachment'
    _description = 'Analytic Account Attachments'

    file = fields.Binary('File')
    file_name = fields.Char('Filename')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    date = fields.Date('Date', default=fields.Date.context_today)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Contract')

AccountAnalyticAttachment()

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    attachment_ids = fields.One2many('account.analytic.attachment', 'analytic_account_id', 'Attachments')

AccountAnalyticAccount()
