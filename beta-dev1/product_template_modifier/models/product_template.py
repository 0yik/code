# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_template_modifier(models.Model):
    _inherit = 'product.template'

    rfid = fields.Char('RFID Code')

    @api.model
    def create(self, values):
        res = super(product_template_modifier, self).create(values)
        if 'rfid' in values and res:
            product_product_obj = self.env['product.product'].search([('product_tmpl_id', '=', res.id)])
            product_product_obj.rfid = values.get('rfid')
        return res

    @api.multi
    def write(self, values):
        res = super(product_template_modifier, self).write(values)
        if 'rfid' in values and res:
            product_product_obj = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
            product_product_obj.rfid = values.get('rfid')
        return res