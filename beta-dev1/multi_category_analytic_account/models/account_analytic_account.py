# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    analytic_ctg = fields.Many2one('account.analytic.category', string='Analytic Category' )