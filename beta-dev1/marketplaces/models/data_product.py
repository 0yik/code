# -*- coding: utf-8 -*-

from odoo import models, fields, api

class data_product(models.Model):
    _name = 'marketplaces.data.product'
    _inherit = 'product.template'

    name = fields.Char('Name')
    line_ids = fields.One2many('marketplaces.data.product.line', 'parent_id', string='Attributes')

    @api.model
    def check(self, record, values):
        product_template_obj = self.env['product.template']
        item = {
            'name': values['name'],
            'marketplace_id': record.id,
        }
        existed = product_template_obj.search([('marketplace_id', '=', record.id)])
        if existed and len(existed) > 0:
            existed.write(item)
        else:
            product_template_obj.create(item)
        True

    @api.model
    def create(self, values):
        result = super(data_product, self).create(values)
        self.check(result, values)
        return result

    @api.multi
    def write(self, values):
        result = super(data_product, self).write(values)
        for record in self:
            self.check(record, values)
        return result

class data_product_line(models.Model):
    _name = 'marketplaces.data.product.line'

    parent_id = fields.Many2one('marketplaces.data.product', 'Product')
    attribute_id = fields.Many2one('marketplaces.data.product.attribute', string='Attribute')
    attribute_name = fields.Char(related='attribute_id.name', string='Name')
    value = fields.Char('Value')

class product_template(models.Model):
    _inherit = 'product.template'

    marketplace_id = fields.Many2one('marketplaces.data.product', 'Market Place')