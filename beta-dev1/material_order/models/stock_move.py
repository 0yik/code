# -*- coding: utf-8 -*-
from openerp import api, fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    # brand_id = fields.Many2many('product.brand', string="Brand")

StockMove()