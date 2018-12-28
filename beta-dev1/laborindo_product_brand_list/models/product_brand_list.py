# coding=utf-8
# coding=utf-8
from odoo import api, fields, models, _


class ProductBrandList(models.Model):
    _name = 'product.brand.list'

    name = fields.Char(string='Brand')

class ProductCategoryList(models.Model):
    _name = 'product.category.list'

    name = fields.Char(string='Category')
    brand_id = fields.Many2one('product.brand.list', string='Brand')

class ProductSubCategoryList(models.Model):
    _name = 'product.sub.category.list'

    name = fields.Char(string='Sub Category')
    category_id = fields.Many2one('product.category.list', string='Category')
    brand_id = fields.Many2one('product.brand.list', string='Brand')

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            self.brand_id = self.category_id.brand_id.id
