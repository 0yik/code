# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCustomCategory(models.Model):
    _name = "product.custom.category"

    name = fields.Char(string='Name')

class Product(models.Model):
    _inherit = "product.template"

    code = fields.Char('Code')
    no_pom = fields.Char('No.POM')
    sap = fields.Char('SAP')
    alias = fields.Char('Alias')
    brand_id = fields.Many2one('brand.brand', string='Brand')
    movement = fields.Selection([('new','New'),('discontinue','Discontinue'),('running','Running'),('slow','Slow')])
    product_category_ids = fields.Many2many('product.custom.category', 'product_id', 'category_id', string='Product Category')
    type = fields.Selection([('consu', 'Consumable'), ('service', 'Service'), ('product', 'Stockable Product')],default='product')