# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    show_dropdown = fields.Boolean('Selectable', default=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        args += [('show_dropdown', '=', True)]
        return super(AccountAnalyticAccount, self).name_search(name, args=args, operator=operator, limit=limit)