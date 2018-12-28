# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    nett_weight = fields.Float('Nett Weight', default=0.0)
    gross_weight = fields.Float('Gross Weight', default=0.0)