# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_ctg = fields.Selection([('ppic', 'PPIC'), ('non_ppic', 'Non-PPIC')],default='ppic',string='Product Category')