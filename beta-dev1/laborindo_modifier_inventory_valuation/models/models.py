# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Quant(models.Model):
    _inherit = 'stock.quant'

    uom_so_id = fields.Many2one('product.uom', related='product_id.product_tmpl_id.uom_so_id')
    qty_sale = fields.Float("Quantity for Sale",compute='_compute_qty_sale',)

    @api.one
    def _compute_qty_sale(self):
        """ Compute Quantity from unit measure bigger ratio"""
        if self.qty > 0 and  self.product_id.uom_so_id.factor_inv:
        	self.qty_sale = self.qty / self.product_id.uom_so_id.factor_inv

