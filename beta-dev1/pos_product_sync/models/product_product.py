# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_product(models.Model):
    _inherit = 'product.product'

    external_id = fields.Integer('External ID')