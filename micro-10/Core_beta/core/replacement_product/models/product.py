# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class product_template(models.Model):
    _inherit = 'product.template'

    replacement_product_ids = fields.One2many('product.replacement', 'product_ref_id', string="Replacement Product")

product_template()

class product_replacement(models.Model):
    _name = 'product.replacement'
    _rec_name = 'product_id'

    product_ref_id = fields.Many2one('product.template', string="Product Template ref")
    product_id = fields.Many2one('product.product', string="Product")
    uom_id = fields.Many2one('product.uom', string="UOM")

product_replacement()