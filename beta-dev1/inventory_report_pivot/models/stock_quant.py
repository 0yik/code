# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Quant(models.Model):
    _inherit = 'stock.quant'

    branch_id = fields.Char(related='product_id.branch_ids.name', relation='res.branch', string="Branch", store=True)
    city_id = fields.Char(related='product_id.branch_ids.city_id.name', relation='city.city', string="City", store=True)
    brand_id = fields.Char(string='Brand', related='product_id.brand_ids.name',  relation='product.brand', store=True)

Quant()
