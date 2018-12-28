# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_location_inherit(models.Model):
    _inherit = 'stock.location'


    inventory_summary = fields.Boolean(string = 'Inventory Summary')