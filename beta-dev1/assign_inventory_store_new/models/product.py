# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class Product(models.Model):
    _inherit = 'product.product'

    qty_min_store = fields.Integer(
        string='Min Qty for store', help='')
    qty_new_store = fields.Integer(
        string='New Qty for store', help='')
    qty_warehouse = fields.Integer(
        string='New Qty for Warehouse', help='')
    

Product()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qty_min_store = fields.Integer(
        string='Min Qty for store', help='')
    qty_new_store = fields.Integer(
        string='New Qty for store', help='')
    qty_warehouse = fields.Integer(
        string='New Qty for Warehouse', help='')

ProductTemplate()
