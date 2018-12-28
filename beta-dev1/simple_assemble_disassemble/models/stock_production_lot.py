# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    material_ids = fields.Many2many('assemble.materials', string='Materials')

StockProductionLot()