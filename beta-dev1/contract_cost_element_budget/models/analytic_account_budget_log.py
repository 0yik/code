# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AnalyticAccountBudgetLog(models.Model):
    _name = 'account.analytic.account.budget.log'

    old_budget   = fields.Float('Old Budget', readonly=True)
    new_budget   = fields.Float('New Budget', readonly=True)
    remarks      = fields.Text('Remarks', readonly=True)
    date         = fields.Date('Date', readonly=True)
    budge_change_number = fields.Char('Budget Change Reference')

    user_id         = fields.Many2one('res.users', 'User', readonly=True)
    cost_element_id = fields.Many2one('project.cost_element', 'Cost Element', readonly=True)
    account_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)