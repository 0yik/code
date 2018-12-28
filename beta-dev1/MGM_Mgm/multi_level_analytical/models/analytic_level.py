# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountAnalyticLevel(models.Model):
    _name = 'account.analytic.level'

    @api.multi
    def compute_analytic_count(self):
        for record in self:
            record.analytic_account_count = len(self.env['account.analytic.account'].search([('level_id','=',record.id)]))

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    analytic_account_count = fields.Integer(compute='compute_analytic_count', string='# of Analytic Accounts')

    @api.multi
    def open_analytic_account(self):
        action = self.env.ref('analytic.action_account_analytic_account_form').read()[0]
        action['domain'] = [('level_id', 'in', self.ids)]
        return action

AccountAnalyticLevel()

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    level_id = fields.Many2one('account.analytic.level', 'Analytic Level')

AccountAnalyticAccount()