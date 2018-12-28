# -*- coding: utf-8 -*-

from odoo import models,api,fields

class stock_product_expiry_line(models.Model):
    _name = 'stock.product.expiry.line'
    
    product_id = fields.Many2one("product.product","Product")
    expiry_days = fields.Integer("Expiry Days Alert",default=-1)
    notification_recipients = fields.Many2many("res.users",'stock_product_expiry_line_res_users_rel','lot_id','user_id','Expiry Notification Recipients')
    location_id = fields.Many2one("stock.location",'Location')
    serial_number = fields.Char("Serial No.")