# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from functools import partial


class PosOrder(models.Model):
    _inherit = "pos.order"

    issuer_id = fields.Many2one('hr.employee', 'Issuer')

    @api.model
    def _order_fields(self, ui_order):
	res = super(PosOrder, self)._order_fields(ui_order)
	res['issuer_id'] = ui_order['issuer_id']
	return res

    def _prepare_invoice(self):
        res = super(PosOrder, self)._prepare_invoice()
	res['issuer_id'] = self.issuer_id.id
	return res
