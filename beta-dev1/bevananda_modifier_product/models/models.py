# -*- coding: utf-8 -*-

from odoo import models, fields, api

class bevananda_modifier_product(models.Model):
    _inherit = 'product.template'

    diameter = fields.Float(string="Diameter")
    size = fields.Float(string="Size")

    