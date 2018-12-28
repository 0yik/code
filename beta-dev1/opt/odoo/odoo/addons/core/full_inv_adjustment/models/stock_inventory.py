# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Inventory(models.Model):
    _inherit = 'stock.inventory'

    new_price = fields.Boolean('Value with new Unit Price')

Inventory()

class InventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.depends('product_qty','theoretical_qty')
    def compute_changes(self):
        for record in self:
            record.change = record.product_qty - record.theoretical_qty

    unit_price = fields.Float('Unit Price')
    new_price = fields.Boolean('Value with new Unit Price', related='inventory_id.new_price')
    change = fields.Float(compute='compute_changes', string='Changes')

InventoryLine()