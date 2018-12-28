# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class product_template(models.Model):
	_inherit = 'product.template'
	
	name = fields.Char('Name', required=True, translate=True, select=True,size=35)
	part_number = fields.Char('Part Number',size=30)
	part_type_id = fields.Many2one('part.type','Part Type')
	alternative_uom_id = fields.Many2one('product.uom','Alternative Unit of Measure')
	drawing_no = fields.Char('Drawing No',size=20)
	revision = fields.Char('Revision')
	customer_code = fields.Many2one('res.partner','Customer Code')
	customer_part_no = fields.Char('Customer Part No')
	add_name_1 = fields.Char('Add Name 1')
	add_name_2 = fields.Char('Add Name 2')
	add_name_3 = fields.Char('Add Name 3')
	add_name_4 = fields.Char('Add Name 4')
