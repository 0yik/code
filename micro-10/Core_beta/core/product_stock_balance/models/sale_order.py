# -*- coding: utf-8 -*-

from odoo import api, models


class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.onchange('user_id')
    def onchange_user_id(self):
        self.ensure_one()
        if self.user_id and self.user_id.default_warehouse:
            self.warehouse_id = self.user_id.default_warehouse
