# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_operation_log(models.Model):
    _name = "stock.operation.log"

    product_id = fields.Many2one('product.product', 'Product')
    is_check   = fields.Boolean('Is check', default= False)
    rfid       = fields.Char('RFID code')
