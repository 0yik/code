# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic Account',
        domain=[])

class PosLine(models.Model):
    _inherit = 'pos.order.line'

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic Account',
        domain=[],store=True)

    @api.model
    def create(self, vals):
        res = super(PosLine, self).create(vals)
        if res.order_id and res.order_id.session_id and res.order_id.session_id.config_id and res.order_id.session_id.config_id.account_analytic_id:
            res.account_analytic_id = res.order_id.session_id.config_id.account_analytic_id
        return res

    @api.multi
    def write(self, vals):
        if self.order_id and self.order_id.session_id and self.order_id.session_id.config_id and self.order_id.session_id.config_id.account_analytic_id:
            vals.update({
                'account_analytic_id' : self.order_id.session_id.config_id and self.order_id.session_id.config_id.account_analytic_id.id
            })

        return super(PosLine, self).write(vals)

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'
    group_analytic_account_for_pos = fields.Boolean('Analytic accounting for Point Of Sale',
        implied_group='pos_analytic_by_config.group_analytic_accounting',
        help="Allows you to specify an analytic account on purchase order lines.")
