# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mgm_modifier_low_stock_notification(models.Model):
    _inherit = 'low.stock.notification.line'

    product_code = fields.Char(string="Product Code")
    unit_of_measure = fields.Many2one('product.uom',string="UoM")

    @api.onchange('product_id')
    def get_product_details(self):
    	self.product_code = self.product_id.default_code
    	self.unit_of_measure = self.product_id.uom_id