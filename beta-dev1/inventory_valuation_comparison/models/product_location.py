# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    location_line = fields.One2many('status.by.location', 'status_by_location_id', string="Location History")

class StatusByLocation(models.Model):
    _name = 'status.by.location'
    _description = 'Stock Status by Location'
    
    status_by_location_id = fields.Many2one('product.product')#O2M
    location_id = fields.Many2one('stock.location', string="Stock Location")
    #SALE
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    so_count = fields.Integer(string='Sale Order Number')
    so_amount = fields.Float(string='Sale Order Amount')
    #PURCHASE
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    po_count = fields.Integer(string='Purchase Order Number')
    po_amount = fields.Float(string='Purchase Order Amount')
    
    so_po_diff_count = fields.Integer(string='Sales – Purchase')
    so_po_diff_amount = fields.Float(string='Sales – Purchase amount')

    stock_move_id = fields.Integer('Stock Move ID')
    date = fields.Date(string='Date')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
