# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    replacement_product_ids = fields.Many2one('product.product', string="Product Subtitution")

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(StockMove, self).onchange_product_id()
        replacement_product_ids = []
        for replacement_obj in self.product_id.replacement_product_ids:
            replacement_product_ids.append(replacement_obj.product_id.id)
        return {'domain': {
            'replacement_product_ids': [('id', 'in',replacement_product_ids)]
        }}
        # self.replacement_product_ids = [(6, 0, replacement_product_ids)]
        # return result

StockMove()