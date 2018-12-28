# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class account_team_member(models.Model):
    _inherit = 'asset.asset.report'

    depreciation_value = fields.Float(string='Accumulative Depreciation', readonly=True)

