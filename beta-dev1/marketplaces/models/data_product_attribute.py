# -*- coding: utf-8 -*-

from odoo import models, fields, api

class data_product_attribute(models.Model):
    _name = 'marketplaces.data.product.attribute'

    name = fields.Char('Name')
    code = fields.Char('Code')
    field_id = fields.Many2one('ir.model.fields', 'Product Field', domain=[('model_id.model', '=', 'product.template')])
