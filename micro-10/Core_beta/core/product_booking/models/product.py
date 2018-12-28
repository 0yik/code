# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProducProduct(models.Model):
    _inherit = 'product.product'
    
    booking_order_line_id = fields.Many2one('booking.order.line',string="Booking Order Line")
    

class ProducTemplate(models.Model):
    _inherit = 'product.template'
    
    default_preparation_days = fields.Integer(string="Default Preparation Days")
    default_buffer_days = fields.Integer(string="Default Buffer Days")
    serial_no = fields.Char(string="Serial No")


