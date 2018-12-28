# -*- coding: utf-8 -*-
from odoo.osv.orm import setup_modifiers
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp

class product_pricelist(models.Model):
	_inherit = 'product.pricelist'

	def _get_partner(self): 
		for line in self.partner_id:
			if line.company_type == 'company':
				self.res_partner_id = line.id

	partner_id = fields.One2many('res.partner', 'property_product_pricelist', string="partner")
	res_partner_id = fields.Many2one('res.partner','Partner', compute="_get_partner")

class product_pricelist_item(models.Model):
	_inherit = 'product.pricelist.item'

	part_number = fields.Many2one('sequence.number.partner','Price History')
	part_number_product = fields.Many2one('sequence.number.product','Part Number')
	drawing_number = fields.Char('Drawing Number')
	pricing_date = fields.Date('Pricing Date')
	quantity_new = fields.Integer('Quantity',default=0)

	@api.multi
	@api.onchange('part_number_product')
	def part_number_product_change(self):
		for part in self:
			self.drawing_number = part.part_number_product.drawing_number

	@api.multi
	@api.onchange('quantity_new')
	def on_changeunit_quantity_new(self):
		for ob in self:
			ob.write({'quantity_new':self.quantity_new})

class res_partner(models.Model):
	_inherit = "res.partner"

	sequence_number = fields.Integer('Sequence',default=0)

class sequence_number_partner(models.Model):
	_name = "sequence.number.partner"

	sequence_id = fields.Many2one('res.partner','Account')
	product_id = fields.Many2one('product.product','Product')
	sequence_number = fields.Integer('Sequence')
	seq_price = fields.Float('Price')
	name = fields.Char('Name')
	pricing_date = fields.Date('Pricing Date')


class sequence_number_product(models.Model):
	_name = "sequence.number.product"

	partner_id = fields.Many2one('res.partner','Account',required=True)
	product_id = fields.Many2one('product.product','Product',required=True)
	drawing_number = fields.Char('Drawing Number',required=True)
	name = fields.Char('Name')
	next_sequence = fields.Integer(compute='compute_sequence',string='Next Sequence')
	expected_number = fields.Integer('Expected Sequence')
	part_type_id = fields.Many2one('part.type','Part Type')
	uom_id = fields.Many2one('product.uom','Unit of Measure')
	lst_price = fields.Float('Price')
	type_id   = fields.Many2one('product.type', 'Product Type')
	product_group = fields.Many2one('product.group.pit','Product Group')
	customer_part_no = fields.Char('Customer Part No')
	part_code = fields.Many2one('part.code.pit','Part Code')
	revision = fields.Char('Revision')
	pricing_date = fields.Date('Pricing Date')

	workpiece_grade = fields.Many2one('workpiece.grade','Workpiece Grade')
	kind_of_machine = fields.Many2one('kind.of.machine','Kind of Machine')
	workpiece_material = fields.Many2one('workpiece.material','Workpiece Material')
	coating_en = fields.Many2one('coating.enquiry','Coating')
	add_name_1 = fields.Char('Add Name 1')
	add_name_2 = fields.Char('Add Name 2')
	add_name_3 = fields.Char('Add Name 3')
	add_name_4 = fields.Char('Add Name 4')
	remarks_en = fields.Text('Remark')

	_sql_constraints = [('name_uniq', 'unique (name)', "Name already exists !")]

	@api.one
	@api.depends('partner_id')
	def compute_sequence(self):
		self.next_sequence = self.partner_id.sequence_number

	@api.model
	def create(self, vals):
		res = super(sequence_number_product,self).create(vals)
		if not vals.get('name'):
			partner_obj = self.env['res.partner'].browse(res.partner_id.id)
			seq_dict = {
				# 'name': str(partner_obj.partner_code) + '-' + str(format(vals.get('expected_number') or partner_obj.sequence_number + 1, '05')),
				'part_type_id':vals.get('part_type_id',False) or res.product_id.part_type_id.id,
				'workpiece_grade':vals.get('workpiece_grade',False) or res.product_id.workpiece_grade.id,
				'kind_of_machine':vals.get('kind_of_machine',False) or res.product_id.kind_of_machine.id,
				'workpiece_material':vals.get('workpiece_material',False) or res.product_id.workpiece_material.id,
				'coating_en':vals.get('coating_en',False) or res.product_id.coating_en.id,
				'add_name_1':vals.get('add_name_1',False) or res.product_id.add_name_1,
				'add_name_2':vals.get('add_name_2',False) or res.product_id.add_name_2,
				'add_name_3':vals.get('add_name_3',False) or res.product_id.add_name_3,
				'add_name_4':vals.get('add_name_4',False) or res.product_id.add_name_4,
				'product_group':vals.get('product_group',False) or res.product_id.product_group.id,
				'customer_part_no':vals.get('customer_part_no',False) or res.product_id.customer_part_no,
				'part_code':vals.get('part_code',False) or res.product_id.part_code.id,
				'uom_id':vals.get('uom_id',False) or res.product_id.uom_id.id,
				'revision':vals.get('revision',False) or res.product_id.revision,
				# 'expected_number':0,
			}
			res.write(seq_dict)
			partner_obj.write({'sequence_number':vals.get('expected_number') or partner_obj.sequence_number + 1})
		return res

	@api.multi
	def write(self, vals):
		partner_obj = self.env['res.partner'].browse(self.partner_id.id)
		if vals.has_key('expected_number') and vals.get('expected_number') != 0:
			vals.update({
				'name': str(partner_obj.partner_code) + '-' + str(format(vals.get('expected_number') or self.expected_number, '05')),
				'expected_number':0,
			})
			print ">>>>>>>>>>>>>>.",vals
			partner_obj.write({'sequence_number':vals.get('expected_number') or partner_obj.sequence_number + 1})
		if vals.has_key('lst_price') and  vals.get('lst_price') != 0:
			part_id = ''
			list_of_part = []
			if partner_obj:
				if partner_obj.sequence_ids:
					for pit in partner_obj.sequence_ids:						
						if pit.product_id.id == self.product_id.id and pit.seq_price != vals.get('lst_price'):
							list_of_part.append(pit.sequence_number)                            
				print "WWWWWWWWWWW", list_of_part
				if list_of_part:
					seq_dict = {
						'name': str(partner_obj.partner_code) + ' - PRICE 0000' + str(max(list_of_part) + 1),
						'sequence_id':partner_obj.id,
						'product_id':self.product_id.id,
						'seq_price':vals.get('lst_price'),
						'sequence_number': max(list_of_part) + 1,
						'pricing_date':fields.Datetime.now(),
					}
					part_id = self.env['sequence.number.partner'].create(seq_dict)
				else:
					seq_dict = {
						'name': str(partner_obj.partner_code) + ' - PRICE 0000' + str(1),
						'sequence_id':partner_obj.id,
						'product_id':vals.get('product_id'),
						'seq_price':vals.get('lst_price'),
						'sequence_number': 1,
						'pricing_date':fields.Datetime.now(),
					}
					part_id = self.env['sequence.number.partner'].create(seq_dict)
		return super(sequence_number_product,self).write(vals)

class crm_lead_line(models.Model):
	_inherit='crm.lead.line'


	@api.model
	def create(self, vals):
		if vals.get('unit_price_en') != 0.0:
			part_id = ''
			list_of_part = []
			partner_obj = self.env['crm.lead'].browse(vals.get('lead_line_id')).partner_id
			if partner_obj:
				if partner_obj.sequence_ids:
					for pit in partner_obj.sequence_ids:
						if not vals.get('part_number'):
							if pit.product_id.id == vals.get('product_en') and pit.seq_price == vals.get('unit_price_en'):
								part_id = pit
							if pit.product_id.id == vals.get('product_en') and pit.seq_price != vals.get('unit_price_en'):
								list_of_part.append(pit.sequence_number)                            
							if pit.product_id.id != vals.get('product_en') and pit.seq_price != vals.get('unit_price_en'):
								print "3333333333333333333",vals.get('unit_price_en')
				
						if vals.get('part_number'):
							if pit.id == vals.get('part_number') and pit.seq_price == vals.get('unit_price_en'):
								part_id = pit

							if pit.id == vals.get('part_number') and pit.seq_price != vals.get('unit_price_en'):
								list_of_part.append(pit.sequence_number)

					if not part_id and not list_of_part:
						seq_dict = {
							'name': str(partner_obj.partner_code) + ' - PRICE 0000' + str(1),
							'sequence_id':partner_obj.id,
							'product_id':vals.get('product_en'),
							'seq_price':vals.get('unit_price_en'),
							'sequence_number': 1,
							'pricing_date':fields.Datetime.now(),
						}
						part_id = self.env['sequence.number.partner'].create(seq_dict)

				else:
					if not partner_obj.sequence_ids:
						seq_dict = {
							'name': str(partner_obj.partner_code) + ' - PRICE 0000' + str(1),
							'sequence_id':partner_obj.id,
							'product_id':vals.get('product_en'),
							'seq_price':vals.get('unit_price_en'),
							'sequence_number': 1,
							'pricing_date':fields.Datetime.now(),
						}
						part_id = self.env['sequence.number.partner'].create(seq_dict)

				if list_of_part:
					seq_dict = {
						'name': str(partner_obj.partner_code) + ' - PRICE 0000' + str(max(list_of_part) + 1),
						'sequence_id':partner_obj.id,
						'product_id':vals.get('product_en'),
						'seq_price':vals.get('unit_price_en'),
						'sequence_number': max(list_of_part) + 1,
						'pricing_date':fields.Datetime.now(),
					}
					part_id = self.env['sequence.number.partner'].create(seq_dict)
				vals.update({'part_number':part_id.id})
		if vals.get('internal_code_en', False):
			part_id = ''
			list_of_part = []
			partner_obj = self.env['res.partner'].browse(vals.get('partner_id'))
			draw_dict = {}
			if partner_obj:
				if partner_obj.drawing_ids:
					for pit in partner_obj.drawing_ids:
						if not vals.get('part_number_product'):
							if pit.product_id.id == vals.get('product_en') and pit.drawing_number == vals.get('internal_code_en'):
								part_id = pit
							if pit.product_id.id == vals.get('product_en') and pit.drawing_number != vals.get('internal_code_en'):
								list_of_part.append(pit.partner_id.sequence_number)                            

						if vals.get('part_number_product'):
							if pit.id == vals.get('part_number_product') and pit.drawing_number == vals.get('internal_code_en'):
								part_id = pit

							if pit.id == vals.get('part_number_product') and pit.drawing_number != vals.get('internal_code_en'):
								list_of_part.append(pit.partner_id.sequence_number)

					if not part_id and not list_of_part:
						seq_dict = {
							'name': str(partner_obj.partner_code) + '-' + str(format(partner_obj.sequence_number + 1, '05')),
							'partner_id':partner_obj.id,
							'product_id':vals.get('product_en'),
							'drawing_number':vals.get('internal_code_en'),
							'part_type_id':vals.get('part_type_id', False),
							'uom_id':vals.get('product_uom', False),
							'lst_price':vals.get('unit_price_en', False),
							'pricing_date':fields.Datetime.now(),
							'workpiece_grade':vals.get('workpiece_grade', False),
							'kind_of_machine':vals.get('kind_of_machine', False),
							'workpiece_material':vals.get('workpiece_material', False),
							'coating_en':vals.get('coating_en',False),
							'add_name_1':vals.get('add_name_1',False),
							'add_name_2':vals.get('add_name_2',False),
						}
						part_id = self.env['sequence.number.product'].create(seq_dict)
						partner_obj.write({'sequence_number': partner_obj.sequence_number + 1})
				else:
					draw_dict = {
						'name': str(partner_obj.partner_code) + '-' + format(partner_obj.sequence_number + 1, '05'),
						'partner_id':partner_obj.id,
						'product_id':vals.get('product_en'),
						'drawing_number':vals.get('internal_code_en'),
						'part_type_id':vals.get('part_type_id', False),
						'uom_id':vals.get('product_uom', False),
						'lst_price':vals.get('unit_price_en', False),
						'pricing_date':fields.Datetime.now(),
						'workpiece_grade':vals.get('workpiece_grade', False),
						'kind_of_machine':vals.get('kind_of_machine', False),
						'workpiece_material':vals.get('workpiece_material', False),
						'coating_en':vals.get('coating_en',False),
						'add_name_1':vals.get('add_name_1',False),
						'add_name_2':vals.get('add_name_2',False),
					}
					part_id = self.env['sequence.number.product'].create(draw_dict)
					partner_obj.write({'sequence_number': partner_obj.sequence_number + 1})
				if list_of_part:
					seq_dict = {
						'name': str(partner_obj.partner_code) + '-' + str(format(max(list_of_part) + 1, '05')),
						'partner_id':partner_obj.id,
						'product_id':vals.get('product_en'),
						'drawing_number':vals.get('internal_code_en'),
						'part_type_id':vals.get('part_type_id', False),
						'uom_id':vals.get('product_uom', False),
						'lst_price':vals.get('unit_price_en', False),
						'pricing_date':fields.Datetime.now(),
						'workpiece_grade':vals.get('workpiece_grade', False),
						'kind_of_machine':vals.get('kind_of_machine', False),
						'workpiece_material':vals.get('workpiece_material', False),
						'coating_en':vals.get('coating_en',False),
						'add_name_1':vals.get('add_name_1',False),
						'add_name_2':vals.get('add_name_2',False),
					}
					part_id = self.env['sequence.number.product'].create(seq_dict)
					partner_obj.write({'sequence_number': max(list_of_part) + 1})
				vals.update({'part_number_product':part_id.id})
		if vals.get('unit_price_en') != 0.0:
			pricelis_dict = {}
			for priclist in self.env['crm.lead'].browse(vals.get('lead_line_id')).partner_id.property_product_pricelist.item_ids:
				if priclist.part_number_product.id == vals.get('part_number_product'):
					pricelis_dict = {
						'item_ids': [(1, priclist.id, {'fixed_price': vals.get('unit_price_en')})]
					}
					priclist.part_number_product.write({'lst_price':vals.get('unit_price_en')})
			if not pricelis_dict:
				pricelis_dict = {
					'item_ids': [(0, 0, {
							'applied_on': '0_product_variant',
							'compute_price': 'fixed',
							'product_id':vals.get('product_en'),
							'fixed_price': vals.get('unit_price_en'),
							'part_number':vals.get('part_number'),
							'drawing_number':vals.get('internal_code_en'),
							'pricing_date':fields.Datetime.now(),
							'part_number_product':vals.get('part_number_product'),
						})]
				}
			vals.update({'pricing_date':fields.Datetime.now()})
			self.env['crm.lead'].browse(vals.get('lead_line_id')).partner_id.property_product_pricelist.write(pricelis_dict)
		return super(crm_lead_line, self).create(vals)

	@api.multi
	def write(self, vals):
		if vals.get('unit_price_en') and vals.get('unit_price_en') != 0.0:
			part_id = ''
			list_of_part = []
			partner_obj = self.lead_line_id.partner_id
			if partner_obj:
				if partner_obj.sequence_ids:
					for pit in partner_obj.sequence_ids:
						if self.part_number and not vals.get('part_number'):
							if pit.product_id.id == self.product_en.id and pit.seq_price == vals.get('unit_price_en'):
								part_id = pit
							if pit.product_id.id == self.product_en.id and pit.seq_price != vals.get('unit_price_en'):
								list_of_part.append(pit.sequence_number)                            
							if self.part_number.id == pit.id and pit.product_id.id != self.product_en.id and pit.seq_price != vals.get('unit_price_en'):
								print "3333333333333333333",vals.get('unit_price_en')
						
						if vals.get('part_number'):
							if pit.id == vals.get('part_number') and pit.seq_price == vals.get('unit_price_en'):
								part_id = pit
							if pit.id == vals.get('part_number') and pit.seq_price != vals.get('unit_price_en'):
								list_of_part.append(pit.sequence_number)

				if not part_id and not list_of_part:
					seq_dict = {
						'name': str(partner_obj.partner_code) + ' - PRICE 0000' + str(1),
						'sequence_id':partner_obj.id,
						'product_id':self.product_en.id,
						'seq_price':vals.get('unit_price_en'),
						'sequence_number': 1,
						'pricing_date':fields.Datetime.now(),
					}
					part_id = self.env['sequence.number.partner'].create(seq_dict)

				if list_of_part:
					seq_dict = {
						'name': str(partner_obj.partner_code) + ' - PRICE 0000' + str(max(list_of_part) + 1),
						'sequence_id':partner_obj.id,
						'product_id':self.product_en.id,
						'seq_price':vals.get('unit_price_en'),
						'sequence_number': max(list_of_part) + 1,
						'pricing_date':fields.Datetime.now(),
					}
					part_id = self.env['sequence.number.partner'].create(seq_dict)
				vals.update({'part_number':part_id.id})
		if vals.get('internal_code_en', False):
			part_id = ''
			list_of_part = []
			partner_obj = self.lead_line_id.partner_id
			if partner_obj:
				if partner_obj.drawing_ids:
					for pit in partner_obj.drawing_ids:
						if self.part_number_product and not vals.get('part_number_product'):
							if pit.product_id.id == self.product_en.id and pit.drawing_number == vals.get('internal_code_en'):
								part_id = pit
							if pit.product_id.id == self.product_en.id and pit.drawing_number != vals.get('internal_code_en'):
								list_of_part.append(pit.partner_id.sequence_number)                            
							if self.part_number_product.id == pit.id and pit.product_id.id != self.product_en.id and pit.drawing_number != vals.get('internal_code_en'):
								pass						
						if vals.get('part_number_product'):
							if pit.id == vals.get('part_number_product') and pit.drawing_number == vals.get('internal_code_en'):
								part_id = pit
							if pit.id == vals.get('part_number_product') and pit.drawing_number != vals.get('internal_code_en'):
								list_of_part.append(pit.partner_id.sequence_number)

					if not part_id and not list_of_part:
						draw_dict = {
							'name': str(partner_obj.partner_code) + '-' + format(partner_obj.sequence_number + 1, '05'),
							'partner_id':partner_obj.id,
							'product_id':self.product_en.id,
							'drawing_number':vals.get('internal_code_en'),
							'uom_id':vals.get('product_uom', False) or self.product_uom.id,
							'lst_price':vals.get('unit_price_en', False) or self.unit_price_en,
							'pricing_date':vals.get('pricing_date', False) or fields.Datetime.now(),
							'workpiece_grade':vals.get('workpiece_grade', False) or self.workpiece_grade.id,
							'kind_of_machine':vals.get('kind_of_machine', False) or self.kind_of_machine.id,
							'workpiece_material':vals.get('workpiece_material', False) or self.workpiece_material.id,
							'coating_en':vals.get('coating_en', False) or self.coating_en.id,
							'add_name_1':vals.get('add_name_1', False) or self.add_name_1,
							'add_name_2':vals.get('add_name_2', False) or self.add_name_2,
						}
						part_id = self.env['sequence.number.product'].create(draw_dict)
						partner_obj.write({'sequence_number': partner_obj.sequence_number + 1})
				else:
					draw_dict = {
						'name': str(partner_obj.partner_code) + '-' + format(partner_obj.sequence_number + 1, '05'),
						'partner_id':partner_obj.id,
						'product_id':self.product_en.id,
						'drawing_number':vals.get('internal_code_en'),
						'uom_id':vals.get('product_uom', False) or self.product_uom.id,
						'lst_price':vals.get('unit_price_en', False) or self.unit_price_en,
						'pricing_date':vals.get('pricing_date', False) or fields.Datetime.now(),
						'workpiece_grade':vals.get('workpiece_grade', False) or self.workpiece_grade.id,
						'kind_of_machine':vals.get('kind_of_machine', False) or self.kind_of_machine.id,
						'workpiece_material':vals.get('workpiece_material', False) or self.workpiece_material.id,
						'coating_en':vals.get('coating_en', False) or self.coating_en.id,
						'add_name_1':vals.get('add_name_1', False) or self.add_name_1,
						'add_name_2':vals.get('add_name_2', False) or self.add_name_2,
					}
					part_id = self.env['sequence.number.product'].create(draw_dict)
					partner_obj.write({'sequence_number': partner_obj.sequence_number + 1})
				if list_of_part:
					draw_dict = {
						'name': str(partner_obj.partner_code) + '-' + str(format(max(list_of_part) + 1, '05')),
						'partner_id':partner_obj.id,
						'product_id':self.product_en.id,
						'drawing_number':vals.get('internal_code_en'),
						'uom_id':vals.get('product_uom', False) or self.product_uom.id,
						'lst_price':vals.get('unit_price_en', False) or self.unit_price_en,
						'pricing_date':vals.get('pricing_date', False) or fields.Datetime.now(),
						'workpiece_grade':vals.get('workpiece_grade', False) or self.workpiece_grade.id,
						'kind_of_machine':vals.get('kind_of_machine', False) or self.kind_of_machine.id,
						'workpiece_material':vals.get('workpiece_material', False) or self.workpiece_material.id,
						'coating_en':vals.get('coating_en', False) or self.coating_en.id,
						'add_name_1':vals.get('add_name_1', False) or self.add_name_1,
						'add_name_2':vals.get('add_name_2', False) or self.add_name_2,
					}
					part_id = self.env['sequence.number.product'].create(draw_dict)
					partner_obj.write({'sequence_number': max(list_of_part) + 1})
				vals.update({'part_number_product':part_id.id})
		if vals.get('unit_price_en') or vals.get('internal_code_en'):
			pricelis_dict = {}
			for priclist in self.lead_line_id.partner_id.property_product_pricelist.item_ids:
				if not vals.get('part_number_product') and priclist.part_number_product.id == self.part_number_product.id:
					pricelis_dict = {
						'item_ids': [(1, priclist.id, {'fixed_price': vals.get('unit_price_en')})]
					}
				if vals.get('part_number_product') and priclist.part_number_product.id == vals.get('part_number_product'):
					pricelis_dict = {
						'item_ids': [(1, priclist.id, {'fixed_price': vals.get('unit_price_en')})]
					}
			if not pricelis_dict:
				pricelis_dict = {
					'item_ids': [(0, 0, {
							'applied_on': '0_product_variant',
							'compute_price': 'fixed',
							'product_id':self.product_en.id,
							'fixed_price': vals.get('unit_price_en'),
							'part_number':vals.get('part_number') or self.part_number.id,
							'drawing_number':vals.get('internal_code_en') or self.internal_code_en,
							'pricing_date':fields.Datetime.now(),
							'part_number_product':vals.get('part_number_product') or self.part_number_product.id,
						})]
				}
			part_product = self.env['sequence.number.product'].browse(vals.get('part_number_product') or self.part_number_product.id)
			part_product.write({'lst_price':vals.get('unit_price_en')})
			if not vals.get('pricing_date'):
				vals.update({'pricing_date':fields.Datetime.now()})
			self.lead_line_id.partner_id.property_product_pricelist.write(pricelis_dict)
		return super(crm_lead_line, self).write(vals)

	@api.multi
	@api.onchange('unit_price_en')
	def on_changeunit_price_en(self):
		for ob in self:
			self.pricing_date = fields.Datetime.now()

	@api.multi
	@api.onchange('part_number')
	def part_number_change(self):
		for part in self:
			values = {
				'unit_price_en': part.part_number.seq_price,
				'pricing_date': part.part_number.pricing_date,
			}
		self.update(values)

	@api.multi
	@api.onchange('part_number_product')
	def part_number_product_change(self):
		for part in self:
			self.internal_code_en = part.part_number_product.drawing_number
		vals = {}
		if part:
			vals['workpiece_grade'] = self.part_number_product.workpiece_grade.id
			vals['kind_of_machine'] = self.part_number_product.kind_of_machine.id
			vals['coating_en'] = self.part_number_product.coating_en.id
			vals['workpiece_material'] = self.part_number_product.workpiece_material.id
			vals['internal_code_en'] = self.part_number_product.drawing_number
			vals['add_name_1'] = self.part_number_product.add_name_1
			vals['add_name_2'] = self.part_number_product.add_name_2
			vals['unit_price_en'] = self.part_number_product.lst_price
		self.update(vals)

	@api.multi
	def _get_display_price(self, product):
		product_context = {}
		product_context['pricelist'] = self.lead_line_id.partner_id.property_product_pricelist.id
		price = product.with_context(product_context).price
		return price


	@api.multi
	@api.onchange('product_en')
	def product_id_change(self):
		vals = {}
		
		if not self.product_en:
			return {'domain': {'product_uom': []}}

		vals = {}
		domain = {'product_uom': [('category_id', '=', self.product_en.uom_id.category_id.id)]}
		if not self.product_uom or (self.product_en.uom_id.id != self.product_uom.id):
			vals['product_uom'] = self.product_en.uom_id

		product = self.product_en.with_context(
			lang=self.lead_line_id.partner_id.lang,
			partner=self.lead_line_id.partner_id.id,
			pricelist=self.lead_line_id.partner_id.property_product_pricelist.id,
			quantity=vals.get('qty_en') or self.qty_en,
		)
		vals['qty_en'] = 1.0
		name =''
		if product:
			vals['remarks_en'] = product.pro_remark

		if product.description_sale:
			name += '\n' + product.description_sale
		vals['remarks_en'] = name
		if product:
			vals['unit_price_en'] = 0.0
		self.update(vals)