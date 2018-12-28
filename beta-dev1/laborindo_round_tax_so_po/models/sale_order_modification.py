# coding=utf-8
from odoo import api, fields, models, _

class SaleOrderLineModification(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        res = super(SaleOrderLineModification, self)._compute_amount()
        for line in self:
            line.price_subtotal = round(line.price_subtotal)
            line.price_tax = round(line.price_tax)
        # 2/0
        return res
