# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stockt_standard(models.Model):
    _name = 'stock.buffer'

    name = fields.Char(string='Name')
    location_id = fields.Many2one('stock.location', string="Location")
    stockt_buffer_line = fields.One2many('stock.buffer.line', 'stock_buffer_id', string='Stock Standard Lines', copy=True)

class stockt_standard_line(models.Model):
    _name = 'stock.buffer.line'

    stock_buffer_id = fields.Many2one('stock.buffer', string='Stock Standard', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)
    product_id_code = fields.Char('Product Code', related='product_id.default_code')
    stock_buffer_amount = fields.Float('Stock Buffet')

    @api.onchange('product_id_code')
    def onchange_product_id_code(self):
        if self.product_id_code:
            product = self.env['product.product'].search([('default_code','=',self.product_id_code)], limit=1)
            if product and product != self.product_id:
                self.product_id = product
