# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    cost_element_ids = fields.One2many('account.analytic.account.cost.element', 'account_analytic_account_id', 'Cost Element')
    budget_log_ids   = fields.One2many('account.analytic.account.budget.log', 'account_analytic_account_id', 'Budget Log Changes')