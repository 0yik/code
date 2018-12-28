# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class CustomProductProduct(models.Model):
    _inherit = 'product.template'

    has_expiry = fields.Boolean('Has Expiry', required=False)
    gift_wrap = fields.Boolean('Gift Wrap', required=False)
    is_liquid = fields.Boolean('Is Liquid', required=False)
    isbn = fields.Char('ISBN', required=False)
    special_discount = fields.Float('Special Discount', required=False)
    global_discount = fields.Float('Global Discount', required=False)
    height = fields.Float('Height', required=False)
    viewed = fields.Integer('Viewed', required=False)
    jan = fields.Char('JAN', required=False)
    width = fields.Float('Width', required=False)
    is_upc_checked = fields.Boolean('Is UPC Checked', required=False)
    mpn = fields.Char(string='MPN', readonly=False)
    offerPriceFormatted = fields.Char('Offer Price', required=False)
    product_id = fields.Char(string='Product ID', readonly=False)
    model = fields.Char(string='Model', readonly=False)
    upc = fields.Char(string='UPC', readonly=False)
    length = fields.Float('Length', required=False)
    minimum = fields.Float(string='Minimum', readonly=False)
    level = fields.Boolean(string='Level', readonly=False)
    brand_name = fields.Char(string='Brand Name', readonly=False)
    has_option = fields.Boolean(string='Has Option', readonly=False)
    sku=fields.Char(string="SKU", readonly=True)

class CustomProductCategory(models.Model):
    _inherit = 'product.category'

    name = fields.Char('Name', required=True, translate=True, index=True)

    _sql_constraints = [
        ('uniq_name_1', 'unique(name)',
         "A Category already exists with this name . Category name must be unique !"),
    ]
