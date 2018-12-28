# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _prepare_analytic_account(self, line):
        # return line.order_id.session_id.config_id.account_analytic_id.id
        return line.account_analytic_id.id