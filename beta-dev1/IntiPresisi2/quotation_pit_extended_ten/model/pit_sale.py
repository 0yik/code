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

class res_users(models.Model):
	_inherit = 'res.users'

	@api.multi
	def get_phonecall_ids(self):
		for rc in self:
			result_ids = self.env['crm.phonecall'].search([('user_id','=',rc.id),('date','>=',rc.start_date),('date','<=',rc.end_date)])
			rc.phonelog_ids = self.env['crm.phonecall'].browse([x.id for x in result_ids])
			
	@api.multi
	def get_emails_ids(self):
		rc = ''
		if self:
			rc = self[0]
			result_ids = self.env['mail.mail'].search([('create_uid','=',rc.id),('date','>=',rc.start_date),('date','<=',rc.end_date)])
			rc.email_log_ids = self.env['mail.mail'].browse([x.id for x in result_ids])
				
	@api.multi
	def get_meeting_ids(self):
		for rc in self:
			meeting_ids = []
			self.env.cr.execute(''' select calendar_event_id from calendar_event_res_partner_rel where res_partner_id = %s; '''%rc.partner_id.id)
			kq = self.env.cr.dictfetchall()
			if kq:
				for x in kq:
					calendar_obj = self.env['calendar.event'].browse(x['calendar_event_id'])
					if calendar_obj.start >= rc.start_date and calendar_obj.start <= rc.end_date:
						meeting_ids.append(calendar_obj.id)
				rc.meeting_log_ids = meeting_ids


	phonelog_ids = fields.Many2many('crm.phonecall', 'user_phonecall_rel', 'user_id', 'phonecall_id', compute='get_phonecall_ids', string='Phone Log')
	email_log_ids = fields.Many2many('mail.mail', 'user_email_rel', 'user_id', 'email_id', string='Email Log', compute='get_emails_ids')
	meeting_log_ids = fields.Many2many('calendar.event', 'user_cal_meeting_rel', 'user_id', 'meeting_id', string='Meeting Log',compute='get_meeting_ids')
	start_date = fields.Datetime('Start Date')
	end_date = fields.Datetime('End Date')

class ResCompany(models.Model):
	_inherit = 'res.company'
	
	npwp_no = fields.Char('NPWP No')
	dom = fields.Char('Dom')
	bank_acc_number = fields.Char('Bank Acc No')
	bank_bin = fields.Char('Bank Name')
	sign_line_text = fields.Char('sign Line')

class ProductType(models.Model):
	_name = 'product.type'    
	name = fields.Char('Name', size=256)

class ProductFamily(models.Model):
	_name = 'product.family'
	name = fields.Char('Name', size=256) 

class res_users(models.Model):
	_inherit = 'res.users'

	sales_person_b = fields.Boolean('Sales Person')
	sales_coordinator_b = fields.Boolean('Sales Coordinator')
	technical_support_b = fields.Boolean('Technical Support')
	director_b = fields.Boolean('Director')
	president_director_b = fields.Boolean('President Director')
	admin_b = fields.Boolean('Admin')
	sales_supervisor_b = fields.Boolean('Sales Supervisor')


class sale_order(models.Model):
	_inherit = 'sale.order'
	
	@api.multi
	def action_quotation_send_stage(self):
		self.write({'state':'sent'})
		return True

class part_code_pit(models.Model):
	_name = 'part.code.pit'

	name = fields.Char('Part Code')

class product_group_pit(models.Model):
	_name = 'product.group.pit'

	name = fields.Char('Product Group')

class product_template(models.Model):
	_inherit = 'product.template'

	workpiece_grade = fields.Many2one('workpiece.grade','Workpiece Grade')
	kind_of_machine = fields.Many2one('kind.of.machine','Kind of Machine')
	part_code = fields.Many2one('part.code.pit','Part Code')
	product_group = fields.Many2one('product.group.pit','Product Group')
	type_id   = fields.Many2one('product.type', 'Product Type')
	workpiece_material = fields.Many2one('workpiece.material','Workpiece Material')
	coating_en = fields.Many2one('coating.enquiry','Coating')
	pricing_date = fields.Date('Pricing Date')
	pro_remark = fields.Text('Remarks')

	family_id = fields.Many2one('product.family', 'Product Family')
	fproduct_ids = fields.Many2many('product.product', 'template_variant_rel', 'template_id', 'product_id', 'Family Product List')
	productf_id = fields.One2many('product.product', 'fproduct_id', 'Family Product List')
	is_variant = fields.Boolean('Is Variant')
	is_template = fields.Boolean('Is Template')
	

class crm_stage(models.Model):
	_inherit = 'crm.stage'

	stage_known = fields.Integer('Stage Num')

	
class product_product(models.Model):
	_inherit = 'product.product'

	@api.depends('total_part_qty')
	def _compute_part_count(self):
		part_obj = self.env['sequence.number.product']
		for i in self.ids:
			total_count = 0
			i_obj= ''
			total_count = part_obj.search_count([('product_id','=',i)])
			i_obj = self.env['product.product'].browse(i)
			i_obj.update({'total_part_qty':total_count})

	family_id = fields.Many2one('product.family', 'Product Family')
	fproduct_id = fields.Many2one('product.template', 'Product Family')
	part_num_ids = fields.One2many('sequence.number.product','product_id','Part Number')
	total_part_qty = fields.Integer('Qty',compute='_compute_part_count')


	@api.model
	def create(self, vals):
		res = super(product_product,self).create(vals)
		if vals.get('customer_code') and vals.get('drawing_no'):
			partner_obj = self.env['res.partner'].browse(vals.get('customer_code'))
			seq_dict = {
				'name': str(partner_obj.partner_code) + '-' + str(format(partner_obj.sequence_number + 1, '05')),
				'partner_id':partner_obj.id,
				'product_id':res.id,
				'drawing_number':vals.get('drawing_no'),
				'part_type_id':vals.get('part_type_id', False),
				'uom_id':res.uom_id.id,
				'lst_price':res.lst_price,
				'pricing_date':fields.Datetime.now(),
				'workpiece_grade':vals.get('workpiece_grade', False),
				'kind_of_machine':vals.get('kind_of_machine', False),
				'workpiece_material':vals.get('workpiece_material', False),
				'coating_en':vals.get('coating_en',False),
				'add_name_1':vals.get('add_name_1',False),
				'add_name_2':vals.get('add_name_2',False),
				'add_name_3':vals.get('add_name_3',False),
				'add_name_4':vals.get('add_name_4',False),
				'product_group':vals.get('product_group',False),
				'customer_part_no':vals.get('customer_part_no',False),
				'part_code':vals.get('part_code',False),
				'uom_id':vals.get('uom_id',False),
				'revision':vals.get('revision',False),
			}
			part_id = self.env['sequence.number.product'].create(seq_dict)
			partner_obj.write({'sequence_number': partner_obj.sequence_number + 1})
		return res