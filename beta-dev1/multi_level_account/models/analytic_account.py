# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models, _



class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    is_multi_level = fields.Boolean(
        string='Multi Level Analytic Account', help='Multi Level')
    analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account', help='')
    analytic_level_id = fields.Many2one(
        comodel_name='multi.level.aa',
        string='Analytic Level', help='select level of aa.')
    parent_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Parent Analytic Account', help='')
    unit = fields.Char(string='Unit', size=20, help='Unit name.')


AnalyticAccount()
