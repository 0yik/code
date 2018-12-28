# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    discount = fields.Float("Discount", default=0.0)
    grand_total = fields.Float("Grand Total", compute='compute_grand_total', readonly=True)

    @api.multi
    def compute_grand_total(self):
        for order in self:
            order.grand_total = order.amount_total - order.discount

    @api.model
    def _order_fields(self, ui_order):
        fields_return = super(PosOrder, self)._order_fields(ui_order)
        fields_return.update({
            'discount': ui_order.get('discount') or 0,
            'grand_total': ui_order.get('grand_total') or 0,
        })
        return fields_return

    def test_paid(self):
        """A Point of Sale is paid when the sum
        @return: True
        """
        for order in self:
            if order.lines and not order.amount_total:
                continue
            if (not order.lines) or (not order.statement_ids) or (abs(order.amount_total - order.amount_paid - order.discount) > 0.00001):
                return False
        return True

