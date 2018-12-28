# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ArkcoModifierWarehouseForm(models.Model):
    _inherit = 'stock.warehouse'

    row = fields.Char(string="Row", help="Number of Rows")
    column = fields.Char(string="Column", help="Number of Columns")
    cell = fields.Char(string="Cell", compute="_get_cell")

    @api.depends('row', 'column')
    def _get_cell(self):
    	for rec in self:
    		if rec.row and rec.column:
        		rec.cell = int(rec.row) * int(rec.column)
        	else:
        		pass