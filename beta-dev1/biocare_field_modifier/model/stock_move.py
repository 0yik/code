# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('type', 'in', ['product', 'consu']),
                ('is_equipment', '=', False),
                ], index=True, required=True,
        states={'done': [('readonly', True)]})
