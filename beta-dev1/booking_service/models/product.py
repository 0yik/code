# -*- coding: utf-8 -*-

from odoo import models,fields

class product_template(models.Model):
    _inherit = 'product.template'
    
    is_an_equipment = fields.Boolean("Is an equipment")
    