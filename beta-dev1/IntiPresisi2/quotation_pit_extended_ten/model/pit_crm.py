# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
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


def int_to_roman(input):
	if type(input) != type(1):
		raise TypeError, 'expected integer, got %s' % type(input)
	if not 0 < input < 4000:
		raise ValueError, 'Argument must be between 1 and 3999'
	ints = (
		1000,
		900,
		500,
		400,
		100,
		90,
		50,
		40,
		10,
		9,
		5,
		4,
		1,
		)
	nums = (
		'M',
		'CM',
		'D',
		'CD',
		'C',
		'XC',
		'L',
		'XL',
		'X',
		'IX',
		'V',
		'IV',
		'I',
		)
	result = ''
	for i in range(len(ints)):
		count = int(input / ints[i])
		result += nums[i] * count
		input -= ints[i] * count
	return result


def roman_to_int(input):
	if type(input) != type(''):
		raise TypeError, 'expected string, got %s' % type(input)
	input = input.upper()
	nums = [
		'M',
		'D',
		'C',
		'L',
		'X',
		'V',
		'I',
		]
	ints = [
		1000,
		500,
		100,
		50,
		10,
		5,
		1,
		]
	places = []
	for c in input:
		if not c in nums:
			raise ValueError, 'input is not a valid roman numeral: %s' \
				% input
	for i in range(len(input)):
		c = input[i]
		value = ints[nums.index(c)]

	  # If the next place holds a larger number, this value is negative.

		try:
			nextvalue = ints[nums.index(input[i + 1])]
			if nextvalue > value:
				value *= -1
		except IndexError:

		 # there is no next place.

			pass
		places.append(value)
	sum = 0
	for n in places:
		sum += n

   # Easiest test for validity...

	if int_to_roman(sum) == input:
		return sum
	else:
		raise ValueError, 'input is not a valid roman numeral: %s' \
			% input

class prospect_source(models.Model):
	_name='prospect.source'
	
	name = fields.Char('Prospect Source Name')
	# prospect_source_ids = fields.One2many('crm.lead','prospect_source','Lead')

class industry_source(models.Model):
	_name = 'industry.source'
	
	name = fields.Char('Industry Name')
	# indus_ids = fields.One2many('crm.lead','industry_source_id','Lead')

class qty_machine(models.Model):
	_name = 'qty.machine'
	
	name = fields.Char('Name')
	# q_machine_ids = fields.One2many('crm.lead','quantity_of_machine','Lead')

class prospect_production(models.Model):
	_name = 'prospect.production'
	
	name = fields.Char('Name')
	# prospect_production_ids = fields.One2many('crm.lead','prospect_production','Lead')

class customer_group(models.Model):
	_name = 'customer.group'
	
	name = fields.Char('Name')
	# customer_group_ids = fields.One2many('res.partner','customer_group_id','Lead')

class enquiry_status(models.Model):
	_name = 'enquiry.status'
	
	name = fields.Char('Name')
	# en_status_ids = fields.One2many('crm.lead','en_status','status')

class workpiece_material(models.Model):
	_name = 'workpiece.material'
	
	name = fields.Char('Name')
	# workpiece_ids = fields.One2many('crm.lead','workpiece_material','Workpiece Material')

class coating_enquiry(models.Model):
	_name = 'coating.enquiry'
	
	name = fields.Char('Name')
	# coating_en_ids = fields.One2many('crm.lead','coating_en','Coating')

class attachment_type_en(models.Model):
	_name = 'attachment.type.en'
	
	name = fields.Char('Name')
	# attachment_type_en_ids = fields.One2many('crm.lead','attachment_type_id','Type')

class workpiece_grade(models.Model):
	_name = 'workpiece.grade'

	name = fields.Char('Name')

class part_type(models.Model):
	_name = 'part.type'
	_description = 'Part Type'
	
	name = fields.Char('Name', required=True, translate=True)

class kind_of_machine(models.Model):
	_name = 'kind.of.machine'

	name = fields.Char('Name')

class crm_new_case(models.Model):
	_name = 'crm.new.case'
	
	name = fields.Char('Name')

class phonecall_contact(models.Model):
	_name='phonecall.contact'

	name = fields.Char('Contact')

class vat_code(models.Model):
	_name='vat.code'

	name = fields.Char('Vat Code')

class attachment_enquiry(models.Model):
	_name = 'attachment.enquiry'		
	attach_id = fields.Many2one('crm.lead','Lead')
	attachment_en = fields.Binary('Attachment')
	attachment_type_id = fields.Many2one('attachment.type.en','Type')
	title_attach = fields.Char('Title')
	last_modified_attach = fields.Datetime('Last Modified')
	created_by_attch = fields.Many2one('res.users','Created By',default=lambda self: self.env.user)

class MailTemplate(models.Model):
	_inherit = "mail.template"
	_description = 'Email Templates'
	
	@api.multi
	def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None):
		email_values = email_values or {}
		if isinstance(force_send, list):
			email_values['recipient_ids'] = [(4, pid) for pid in force_send]
			force_send = False
		return super(MailTemplate,self).send_mail(res_id, force_send, raise_exception,email_values)

class mail_message(models.Model):
	_inherit = 'mail.message'

	@api.model
	def _find_allowed_doc_ids(self, model_ids):
	    IrModelAccess = self.env['ir.model.access']
	    user_obj = self.env['res.users'].browse(self._uid)
	    allowed_ids = set()
	    for doc_model, doc_dict in model_ids.iteritems():
	        if not IrModelAccess.check(doc_model, 'read', False):
	            continue
	        if user_obj.admin_b == True or user_obj.president_director_b == True:
	        	continue
	        else:
	        	allowed_ids |= self._find_allowed_model_wise(doc_model, doc_dict)
	    return allowed_ids

class mail_mail(models.Model):
	_inherit = 'mail.mail'

	@api.model
	def search(self, args, offset=0, limit=0, order=None, count=False):
		user_obj = self.env['res.users'].browse(self._uid)
		if self._uid == 1:
			args = []

		if user_obj.sales_supervisor_b == True or user_obj.admin_b == True or user_obj.president_director_b == True:
			args = []
		# offset, limit, order and count must be treated separately as we may need to deal with virtual ids
		events = super(mail_mail, self).search(args, offset=0, limit=0, order=None, count=False)
		return events

class crm_phonecall(models.Model):
	_inherit = 'crm.phonecall'

	prospect_id = fields.Many2one('crm.lead','Lead')
	contact_name = fields.Many2one('phonecall.contact','Contact')


	@api.model
	def create(self, vals):
		if 'stage_type' in self._context:
			if self._context['stage_type'] == 'lead':
				vals.update({'prospect_id':self._context['active_id']})
		return super(crm_phonecall, self).create(vals)

	@api.model
	def search(self, args, offset=0, limit=0, order=None, count=False):
		events = super(crm_phonecall, self).search(args, offset=0, limit=0, order=None, count=False)
		user_obj = self.env['res.users'].browse(self._uid)
		if self._uid == 1:
			args = []
		if user_obj.sales_supervisor_b == True or user_obj.admin_b == True or user_obj.president_director_b == True:
			args = []
		# offset, limit, order and count must be treated separately as we may need to deal with virtual ids
		
		return events

class crm_lead(models.Model):
	_inherit = 'crm.lead'

	email_count = fields.Integer("Emails", compute='_compute_emails_count')
	phonecall_count_opp = fields.Integer(compute='_compute_phonecall_count',string="Phonecalls")
	phonecall_count_lead = fields.Integer(compute='_compute_phonecall_count_lead',string="Phonecalls")
	partner_name = fields.Char('Account Name')
	stage_new_pr = fields.Many2one('crm.new.case','Prospects Status')
	prospect_quality = fields.Selection([('a','$'),('b','$$'),('c','$$$'),('d','$$$$'),('e','$$$$$')], 'Prospect Quality')
	website = fields.Char('Website')
	comp_name = fields.Char('Company')
	planned_revenue = fields.Float('Expected Revenue (Amount)', track_visibility='always')

	# Additional Information
	no_of_employee = fields.Integer('No of Employee')
	annual_revenue = fields.Integer('Annual Revenue')
	prospect_source = fields.Many2one('prospect.source','Prospect Source')
	industry_source_id = fields.Many2one('industry.source','Industry')

	# Prospect Scoring:
	special_carbide_tools = fields.Boolean('Special Carbide Tools')
	qty_per_month = fields.Selection([('a','1 - 5'),('b','6 - 10'),('c','11 - 20'),('d','21 - 50'),('e',' = > 50')],'Quantity Per Month')
	quantity_of_machine = fields.Many2one('qty.machine','Quantity of Machine')
	prospect_production = fields.Many2one('prospect.production','Production')
	special_carbide_tools_score = fields.Integer('Special Carbide Tools Score')
	quantity_per_month_score = fields.Integer('Quantity Per Month Score')
	quantity_of_machine_score = fields.Integer('Quantity of Machine Score')
	production_score = fields.Integer('Production Score')
	total_score = fields.Integer('Total Score')

	# Description Information:
	description_prospect = fields.Text('Description')

	# System Information:
	created_by = fields.Many2one('res.users','Created By',default=lambda self: self.env.user)
	last_modified_by = fields.Datetime('Last Modified By')
	company_currency = fields.Many2one(string='Currency', related='pricelist_id.currency_id', readonly=True, relation="res.currency")

	# OPPORTUNITY FIELDS
	en_number = fields.Char('Enquiry Number')
	enquiry_type = fields.Selection([('new_business','New Business'),('existing_business','Existing Business')], 'Enquiry Type')
	# close_date = fields.Date('Close Date')
	stage = fields.Char('Stage')
	en_status = fields.Many2one('enquiry.status','Enquiry Status')
	en_stages = fields.Many2one('crm.stage', string='Enquiry Stage', track_visibility='onchange', index=True,
		domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]",
		group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())

		  # ADDITIONAL INFO
	prospects_source_id = fields.Many2one('prospect.source', 'Prospect Source')
	next_step = fields.Char('Next Step')
	reason_enquiry = fields.Char('Reason')
	our_reference_ids = fields.Many2one('res.partner','Your Reference')

		# NEGOTITION INFORMATION 

	nagotiation_note = fields.Text('Negotiation n Notes')

		# DESCRIPTION INFORMATION

	description_te = fields.Text('Description')

		# SYSTEM INFORMATION
	created_by_en = fields.Many2one('res.users','Created By',default=lambda self: self.env.user)
	last_modified_by_en = fields.Datetime('Last Modified By')

		# Attachments
	attachment_en_ids = fields.One2many('attachment.enquiry','attach_id',string="Attachment")

	lead_line_ids = fields.One2many('crm.lead.line','lead_line_id',string='CRM Lead Line')

	meeting_count_lead = fields.Integer('# Meetings', compute='_compute_meeting_count_lead')

	pricelist_id = fields.Many2one('product.pricelist','Pricelist')


	@api.multi
	def _compute_phonecall_count_lead(self):
		for partner in self:
			partner.phonecall_count_lead = self.env['crm.phonecall'].search_count([('prospect_id','=',self.id)])


	@api.multi
	def _compute_phonecall_count(self):
		for partner in self:
			if partner.partner_id:
				partner.phonecall_count_opp = self.env['crm.phonecall'].search_count([('partner_id', '=', partner.partner_id.id)])

	def _onchange_partner_id_values(self, partner_id):
		""" returns the new values when partner_id has changed """
		if partner_id:
			partner = self.env['res.partner'].browse(partner_id)

			partner_name = partner.parent_id.name
			if not partner_name and partner.is_company:
				partner_name = partner.name
			value = {
				'partner_name': partner_name,
				'contact_name': partner.name if not partner.is_company else False,
				'title': partner.title.id,
				'street': partner.street,
				'street2': partner.street2,
				'city': partner.city,
				'state_id': partner.state_id.id,
				'country_id': partner.country_id.id,
				'email_from': partner.email,
				'phone': partner.phone,
				'mobile': partner.mobile,
				'fax': partner.fax,
				'zip': partner.zip,
				'function': partner.function,
			}
			if self._context:
				if self._context['default_type'] == 'opportunity':
					value.update({'pricelist_id':partner.property_product_pricelist.id})
			return value
		return {}

	@api.onchange('qty_per_month')
	def _onchange_prospect_quality(self):
		for lead in self:
			lead.prospect_quality = self.qty_per_month

	@api.onchange('partner_id')
	def _onchange_partner_id(self):
		values = self._onchange_partner_id_values(self.partner_id.id if self.partner_id else False)
		self.update(values)

	@api.multi
	def _compute_emails_count(self):
		for partner in self:
			partner.email_count = self.env['mail.mail'].search_count([('res_id','in', [partner.id])])

	@api.multi
	def _compute_meeting_count_lead(self):
		meeting_data = self.env['calendar.event'].read_group([('lead_id', 'in', self.ids)], ['lead_id'], ['lead_id'])
		mapped_data = {m['lead_id'][0]: m['lead_id_count'] for m in meeting_data}
		for lead in self:
			lead.meeting_count_lead = mapped_data.get(lead.id, 0)

	@api.multi
	def write(self, vals):
		access_stage_list = []
		access_stage_list_tech = []
		access_stage_list_coordinate = []
		access_stage_list_person = []
		access_stage_list_supervisor = []
		stage_lead_technical_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_technical_check')[1]
		if stage_lead_technical_check:
			access_stage_list.append(stage_lead_technical_check)
			access_stage_list_coordinate.append(stage_lead_technical_check)
			access_stage_list_person.append(stage_lead_technical_check)
			access_stage_list_tech.append(stage_lead_technical_check)
			access_stage_list_supervisor.append(stage_lead_technical_check)

		quotation_list_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_quotations')[1]
		if quotation_list_check:
			access_stage_list.append(quotation_list_check)
		stage_lead_no_offers = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_no_offers')[1]
		if stage_lead_no_offers:
			access_stage_list.append(stage_lead_no_offers)
			access_stage_list_tech.append(stage_lead_no_offers)
			access_stage_list_coordinate.append(stage_lead_no_offers)

		stage_lead_collect_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_collect_data')[1]
		if stage_lead_collect_check:
			access_stage_list_tech.append(stage_lead_collect_check)
			access_stage_list_person.append(stage_lead_collect_check)
			access_stage_list_supervisor.append(stage_lead_collect_check)

		stage_lead_won_check = self.env['ir.model.data'].get_object_reference('crm','stage_lead4')[1]
		if stage_lead_won_check:
			access_stage_list_person.append(stage_lead_won_check)

		stage_lead_pricing_Check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_pricing')[1]
		if stage_lead_pricing_Check:
			access_stage_list_tech.append(stage_lead_pricing_Check)

		# stage change: update date_last_stage_update
		if 'en_stages' in vals:
			vals['stage_id'] = vals.get('en_stages')
		if self.type == 'lead':
			vals['last_modified_by'] = fields.Datetime.now()
		else:
			vals['last_modified_by_en'] = fields.Datetime.now()
		if 'attachment_en' in vals:
			vals['created_by_attch'] = self._uid
			# vals['last_modified_attach'] = fields.Datetime.now()

		if vals.get('stage_id', False):
			login_user = self.env['res.users'].browse(self._uid)
			if login_user.president_director_b == True:
				if vals['stage_id'] and vals['stage_id'] in access_stage_list:
					pass
				else:
					raise UserError(_('You Can Only Move Enquiry to Technical Checking, Quotation and No Offer.'))

			if login_user.technical_support_b == True:
				if vals['stage_id'] and vals['stage_id'] in access_stage_list_tech: 
					pass
				else:
					raise UserError(_('You Can Only Edit Enquiry to Technical Checking, Collect Date , Pricing , No Offer Stage. Please Contact your Administrator.'))

			if login_user.sales_coordinator_b == True:
				if vals['stage_id'] and vals['stage_id'] in access_stage_list_coordinate:
					raise UserError(_('You Dont have Rights to Edit Record in Technical Drawing , No Offer Stage. Please Contact your Administrator.'))
			
			if login_user.sales_supervisor_b == True:
				if vals['stage_id'] and vals['stage_id'] in access_stage_list_supervisor:
					pass
				else:
					raise UserError(_('You have Only Rights to Edit Record in Collect Data and Technical Drawing Stage. Please Contact your Administrator.'))

			if login_user.sales_person_b == True:
				if vals['stage_id'] and vals['stage_id'] in access_stage_list_person:
					pass
				elif self.env['crm.stage'].browse(vals['stage_id']).name == 'Close Lost':
					pass
				else:
					raise UserError(_('You have Only Rights to Edit Record in Collect Data and Technical Drawing Stage. Please Contact your Administrator.'))

		res = super(crm_lead, self).write(vals)
		if self.stage_id:
			if 'stage_id' in vals:
				stage = self.stage_id
				collect_data_list = []
				login_user = self.env['res.users'].browse(self._uid)
				# if login_user.sales_coordinator_b == True:
				# 	collect_data_list.append(login_user.partner_id.id)
				# else:
				# 	collect_list = self.env['res.users'].search(['|',('sales_coordinator_b','=',True),('sales_supervisor_b','=',True)])
				# 	if collect_list:
				# 		for i in collect_list:
				# 			collect_data_list.append(i.partner_id.id)
				collect_list = self.env['res.users'].search([('sales_supervisor_b','=',True)])
				if collect_list:
					for i in collect_list:
						collect_data_list.append(i.partner_id.id)
						
				if login_user.sales_person_b == True:
					collect_data_list.append(login_user.partner_id.id)

				technical_checking_list = []
				technical_list = self.env['res.users'].search([('technical_support_b','=',True)])
				if technical_list:
					for j in technical_list:
						technical_checking_list.append(j.partner_id.id)

				pricing_list = []
				pricing_list_ext = self.env['res.users'].search([('president_director_b','=',True)])
				if pricing_list_ext:
					for k in pricing_list_ext:
						pricing_list.append(k.partner_id.id)

				quotation_list = []
				quotation_list_ext = self.env['res.users'].search([('sales_coordinator_b','=',True)])
				if quotation_list_ext:
					for l in quotation_list_ext:
						quotation_list.append(l.partner_id.id)

				collect_stage = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_collect_data')
				action_id = self.env['ir.model.data'].get_object_reference('crm','crm_lead_action_activities')[1]
				menu_id = self.env['ir.model.data'].get_object_reference('crm','crm_lead_menu_activities')[1]
				if vals['stage_id'] and collect_stage and vals['stage_id'] == collect_stage[1]:
					
					template = self.env.ref('quotation_pit_extended_ten.email_template_collect_data_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
					mail_id = template.send_mail(self.id,collect_data_list)
					self.env['mail.mail'].browse(mail_id).send()

				stage_lead_technical_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_technical_check')
				if vals['stage_id'] and stage_lead_technical_check and vals['stage_id'] == stage_lead_technical_check[1]:
					template = self.env.ref('quotation_pit_extended_ten.email_template_collect_data_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
					tech_mail_id = template.send_mail(self.id,technical_checking_list)
					self.env['mail.mail'].browse(tech_mail_id).send()

				pricing_list_ext_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_pricing')
				if vals['stage_id'] and pricing_list_ext_check and vals['stage_id'] == pricing_list_ext_check[1]:
					template = self.env.ref('quotation_pit_extended_ten.email_template_collect_data_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
					price_mail_id = template.send_mail(self.id,pricing_list)
					self.env['mail.mail'].browse(price_mail_id).send()

				quotation_list_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_quotations')
				if vals['stage_id'] and quotation_list_check and vals['stage_id'] == quotation_list_check[1]:
					template = self.env.ref('quotation_pit_extended_ten.email_template_collect_data_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
					quot_mail_id = template.send_mail(self.id,quotation_list)
					self.env['mail.mail'].browse(quot_mail_id).send()
		return res

	@api.model
	def create(self, vals):
		access_stage_list = []
		access_stage_list_tech = []
		access_stage_list_coordinate = []
		access_stage_list_person = []
		access_stage_list_supervisor = []
		stage_lead_technical_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_technical_check')[1]
		if stage_lead_technical_check:
			access_stage_list.append(stage_lead_technical_check)
			access_stage_list_coordinate.append(stage_lead_technical_check)
			access_stage_list_person.append(stage_lead_technical_check)
			access_stage_list_tech.append(stage_lead_technical_check)
			access_stage_list_supervisor.append(stage_lead_technical_check)

		quotation_list_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_quotations')[1]
		if quotation_list_check:
			access_stage_list.append(quotation_list_check)
		stage_lead_no_offers = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_no_offers')[1]
		if stage_lead_no_offers:
			access_stage_list.append(stage_lead_no_offers)
			access_stage_list_tech.append(stage_lead_no_offers)
			access_stage_list_coordinate.append(stage_lead_no_offers)

		stage_lead_collect_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_collect_data')[1]
		if stage_lead_collect_check:
			access_stage_list_tech.append(stage_lead_collect_check)
			access_stage_list_person.append(stage_lead_collect_check)
			access_stage_list_person.append(stage_lead_collect_check)
			access_stage_list_supervisor.append(stage_lead_collect_check)

		stage_lead_pricing_Check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_pricing')[1]
		if stage_lead_pricing_Check:
			access_stage_list_tech.append(stage_lead_pricing_Check)

		if 'type' in vals:
			if vals['type'] == 'opportunity':
				seq_num = self.env['ir.sequence'].get('crm.lead').split('-')
				vals['en_number'] =  '000' + str(seq_num[0]) + '/Enq-' + str(self.env['res.partner'].browse(vals.get('partner_id')).short_name or '') + '/IPT/' +str(int_to_roman(int(seq_num[1]))) + '/' + str(seq_num[2])
				vals['stage_id'] = vals.get('en_stages')
				login_user = self.env['res.users'].browse(self._uid)
				if login_user.president_director_b == True:
					if vals['stage_id'] and vals['stage_id'] in access_stage_list:
						pass
					else:
						raise UserError(_('You Can Only Move Enquiry to Technical Checking, Quotation and No Offer.'))
				
				if login_user.technical_support_b == True:
					if vals['stage_id'] and vals['stage_id'] in access_stage_list_tech: 
						pass
					else:
						raise UserError(_('You Can Only Edit Enquiry to Technical Checking, Collect Date , Pricing , No Offer Stage. Please Contact your Administrator.'))

				if login_user.sales_coordinator_b == True:
					if vals['stage_id'] and vals['stage_id'] in access_stage_list_coordinate:
						raise UserError(_('You Dont have Rights to Edit Record in Technical Drawing , No Offer Stage. Please Contact your Administrator.'))

				if login_user.sales_supervisor_b == True:
					if vals['stage_id'] and vals['stage_id'] in access_stage_list_supervisor:
						pass
					else:
						raise UserError(_('You Dont have Rights to Edit Record in Collect Data and Technical Drawing Stage. Please Contact your Administrator.'))

				if login_user.sales_person_b == True:
					if vals['stage_id'] and vals['stage_id'] in access_stage_list_person:
						pass
					else:
						raise UserError(_('You have Only Rights to Edit Record in Collect Data and Technical Drawing Stage. Please Contact your Administrator.'))


		res = super(crm_lead, self).create(vals)
		if 'stage_id' in vals:
			collect_data_list = []
			login_user = self.env['res.users'].browse(self._uid)
			if login_user.sales_coordinator_b == True:
				collect_data_list.append(login_user.partner_id.id)
			else:
				collect_list = self.env['res.users'].search([('sales_coordinator_b','=',True),('sales_supervisor_b','=',True)])
				if collect_list:
					for i in collect_list:
						collect_data_list.append(i.partner_id.id)
			
			if login_user.sales_person_b == True:
				collect_data_list.append(login_user.partner_id.id)
			
			technical_checking_list = []
			technical_list = self.env['res.users'].search([('technical_support_b','=',True)])
			if technical_list:
				for j in technical_list:
					technical_checking_list.append(j.partner_id.id)

			pricing_list = []
			pricing_list_ext = self.env['res.users'].search([('president_director_b','=',True)])
			if pricing_list_ext:
				for k in pricing_list_ext:
					pricing_list.append(k.partner_id.id)

			quotation_list = []
			quotation_list_ext = self.env['res.users'].search([('sales_coordinator_b','=',True)])
			if quotation_list_ext:
				for l in quotation_list_ext:
					quotation_list.append(l.partner_id.id)

			action_id = self.env['ir.model.data'].get_object_reference('crm','crm_lead_action_activities')[1]
			menu_id = self.env['ir.model.data'].get_object_reference('crm','crm_lead_menu_activities')[1]
			collect_stage = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_collect_data')
			if vals['stage_id'] and collect_stage and vals['stage_id'] == collect_stage[1]:
				template = self.env.ref('quotation_pit_extended_ten.email_template_collect_data_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
				mail_id = template.send_mail(res.id,collect_data_list)
				self.env['mail.mail'].browse(mail_id).send()

			stage_lead_technical_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_technical_check')
			if vals['stage_id'] and stage_lead_technical_check and vals['stage_id'] == stage_lead_technical_check[1]:
				template = self.env.ref('quotation_pit_extended_ten.email_template_collect_data_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
				tech_mail_id = template.send_mail(res.id,technical_checking_list)
				self.env['mail.mail'].browse(tech_mail_id).send()

			pricing_list_ext_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_pricing')
			if vals['stage_id'] and pricing_list_ext_check and vals['stage_id'] == pricing_list_ext_check[1]:
				template = self.env.ref('quotation_pit_extended_ten.email_template_collect_data_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
				price_mail_id = template.send_mail(res.id,pricing_list)
				self.env['mail.mail'].browse(price_mail_id).send()

			quotation_list_check = self.env['ir.model.data'].get_object_reference('quotation_pit_extended_ten','stage_lead_quotations')
			if vals['stage_id'] and quotation_list_check and vals['stage_id'] == quotation_list_check[1]:
				template = self.env.ref('quotation_pit_extended_ten.email_template_collect_data_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
				quot_mail_id = template.send_mail(res.id,quotation_list)
				self.env['mail.mail'].browse(quot_mail_id).send()
		return res

	@api.model
	def _onchange_stage_id_values(self, stage_id):
		""" returns the new values when stage_id has changed """
		vals = {}
		if not stage_id:
			return {}
		vals['en_stages'] = stage_id
		return vals

	@api.multi
	def action_schedule_meeting(self):
		""" Open meeting's calendar view to schedule meeting on current opportunity.
			:return dict: dictionary value for created Meeting view
		"""
		self.ensure_one()
		action = self.env.ref('calendar.action_calendar_event').read()[0]
		partner_ids = self.env.user.partner_id.ids
		if self.partner_id:
			partner_ids.append(self.partner_id.id)
		action['context'] = {
			# 'search_default_user_id':self.user_id
			'search_default_opportunity_id': self.id if self.type == 'opportunity' else False,
			'default_opportunity_id': self.id if self.type == 'opportunity' else False,
			'default_partner_id': self.partner_id.id,
			'default_partner_ids': partner_ids,
			# 'default_team_id': self.team_id.id,
			# 'default_name': self.name,
		}
		# action['domain'] = { 'user_id' :self.env.user}
		return action


class crm_lead_line(models.Model):
	_name='crm.lead.line'
	_order = 'lead_line_id'

	@api.depends('qty_en', 'discount', 'unit_price_en', 'tax_id')
	def _compute_amount(self):
		"""
		Compute the amounts of the SO line.
		"""
		for line in self:
			price = line.unit_price_en * (1 - (line.discount or 0.0) / 100.0)
			taxes = line.tax_id.compute_all(price, line.currency_id, line.qty_en, product=line.product_en, partner=line.lead_line_id.partner_id)
			line.update({
				'price_tax': taxes['total_included'] - taxes['total_excluded'],
				'total_price_en': taxes['total_included'],
				'price_subtotal': taxes['total_excluded'],
			})

	@api.model
	def _get_partner(self):
		partner = False
		context = self._context or {}
		if context.get('partner_id'):
			partner = context.get('partner_id')
		return partner

	@api.one
	@api.depends('unit_price_en')
	def compute_vissibility(self):
		if self.env.user.director_b == True or self.env.user.technical_support_b == True or self.env.user.sales_coordinator_b == True or self.env.user.sales_supervisor_b == True or self.env.user.sales_person_b == True:
			self.check_uid = True

		# PRODUCT PRICELISTINGt
	
	lead_line_id = fields.Many2one('crm.lead',string='Listing Line',index=True)
	product_en = fields.Many2one('product.product','Product Variant')
	qty_en = fields.Integer('Quantity')
	unit_price_en = fields.Float('Unit Price')
	total_price_en = fields.Float('Total Price')
	part_number = fields.Many2one('sequence.number.partner','Price History')
	tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
	internal_code_en = fields.Char('Internal Code')
	workpiece_material = fields.Many2one('workpiece.material','Workpiece Material')
	coating_en = fields.Many2one('coating.enquiry','Coating')
	product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
	pricing_date = fields.Date('Pricing Date')
	remarks_en = fields.Text('Remarks')
	partner_id = fields.Many2one('res.partner',string='Account' ,default=_get_partner,store=True)
	currency_id = fields.Many2one(related='lead_line_id.partner_id.property_product_pricelist.currency_id', store=True, string='Currency', readonly=True)
	discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
	price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
	price_tax = fields.Monetary(compute='_compute_amount', string='Taxes', readonly=True, store=True)
	total_price_en = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)

	workpiece_grade = fields.Many2one('workpiece.grade','Workpiece Grade')
	kind_of_machine = fields.Many2one('kind.of.machine','Kind of Machine')
	part_number_product = fields.Many2one('sequence.number.product','Part Number')
	check_uid = fields.Boolean(compute='compute_vissibility', string='Users')
	add_name_1 = fields.Char('Add Name 1')
	add_name_2 = fields.Char('Add Name 2')
	part_name = fields.Char('Part Name')

class res_partner(models.Model):
	_inherit = 'res.partner'

	@api.model
	def _get_euro(self):
		return self.env['res.currency.rate'].search([('rate', '=', 1)], limit=1).currency_id

	@api.model
	def _get_user_currency(self):
		currency_id = self.env['res.users'].browse(self._uid).company_id.currency_id
		return currency_id or self._get_euro()


	user_id = fields.Many2one('res.users','Account Owner',default=lambda self: self.env.user)
	sequence_ids = fields.One2many('sequence.number.partner','sequence_id','Sequence')
	drawing_ids = fields.One2many('sequence.number.product','partner_id','Drawing')
	email_count = fields.Integer("Emails", compute='_compute_emails_count')
	partner_code = fields.Char('Code',required=True)
	street_delivery =  fields.Char('Street')
	street2_delivery =  fields.Char('Street2')
	zip_delivery =  fields.Char('Zip', size=24, change_default=True)
	city_delivery =  fields.Char('City')
	state_id_delivery =  fields.Many2one("res.country.state", 'State', ondelete='restrict')
	country_id_delivery =  fields.Many2one('res.country', 'Country', ondelete='restrict')
	mailing_address_name = fields.Char('Mailing Address')
	delivery_address_name = fields.Char('Delivery Address')
	city2_mailing =  fields.Char('City')
	city2_delivery =  fields.Char('City')
	zip2_mailing =  fields.Char('Zip')
	zip2_delivery =  fields.Char('Zip')
	currency_new_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self._get_user_currency())
	customer_group_id = fields.Many2one('customer.group','Customer Group')
	vat_code = fields.Many2one('vat.code','Vat Code')
	vat_number = fields.Char('Vat Number (NPWP No.)')
	country_code = fields.Char('Country Code')
	state_id2 = fields.Many2one("res.country.state", 'State', ondelete='restrict')
	state_id2_delivery = fields.Many2one("res.country.state", 'State', ondelete='restrict')
		# REFERENCE DETAILS
	ref_name = fields.Char('Name')
	ref_phone = fields.Char('Phone')
	ref_mobile = fields.Char('Mobile')
	ref_email = fields.Char('Email')
	short_name = fields.Char('Short Name', required=True)
	acc_type = fields.Selection(string='Account Type',selection=[('local','Local'), ('international', 'International')],default="local")

	_sql_constraints = [('partner_code_uniq', 'unique (partner_code)', "Account Code already exists !")]

	@api.multi
	def onchange_state_delivery(self, state_id):
		if state_id:
			state = self.env['res.country.state'].browse(state_id)
			return {'value': {'country_id_delivery': state.country_id.id}}
		return {}

	@api.multi
	def _compute_emails_count(self):
		for partner in self:
			partner.email_count = self.env['mail.mail'].search_count([('recipient_ids','in', [partner.id])])

	@api.multi
	def write(self,vals):
		for partner in self:
			if vals.get('currency_new_id'):
				partner.property_product_pricelist.write({'currency_id':vals.get('currency_new_id')})
		return super(res_partner,self).write(vals)

	@api.model
	def search(self, args, offset=0, limit=0, order=None, count=False):
		filter_partners = []
		partners = super(res_partner, self).search(args, offset=0, limit=0, order=None, count=False)
		print "DDDDSS",type(partners)
		user_obj = self.env['res.users'].browse(self._uid)
		if partners and user_obj.sales_person_b == True or user_obj.technical_support_b == True:
			for partner in partners:
				if partner.user_id.id != self._uid and partner.company_type == 'company':
					filter_partners.append(partner.id)
			if filter_partners:
				remove_partner = [par.id for par in partners if par.id not in filter_partners]
				partners = self.browse(remove_partner)
		return partners


class location_calnder(models.Model):
	_name = 'location.calnder'

	name = fields.Char('Location Name') 

class CalendarEvent(models.Model):
	_inherit = 'calendar.event'

	lead_id = fields.Many2one('crm.lead', 'Leads', domain="[('type', '=', 'lead')]")
	location_cal_id =fields.Many2one('location.calnder','Location')


	@api.model
	def create(self, vals):
		if 'stage_type' in self._context:
			if self._context['stage_type']:
				vals['lead_id'] = self._context['active_id']
		event = super(CalendarEvent, self).create(vals)
		return event

	# @api.model
	# def search(self, args, offset=0, limit=0, order=None, count=False):
	# 	user_obj = self.env['res.users'].browse(self._uid)
	# 	print "---------------------", args
	# 	if self._uid == 1:
	# 		args = []
	# 	if user_obj.sales_supervisor_b:
	# 		args = []
	# 	# offset, limit, order and count must be treated separately as we may need to deal with virtual ids
	# 	events = super(CalendarEvent, self).search(args, offset=0, limit=0, order=None, count=False)
	# 	return events

class validate_new_date(models.Model):
	_name = 'validate.new.date'

	name = fields.Char('Name')

class sale_order(models.Model):
	_inherit = 'sale.order'

	hide_confirm = fields.Boolean('Hide')
	or_sale_id = fields.Many2one('Origin')
	validity_new_date = fields.Many2one('validate.new.date','Expiration Date')
	po_num = fields.Char('PO Number')
	order_date = fields.Date('Order Date')
	delivery_date = fields.Date('Delivery Date')
	user_id = fields.Many2one('res.users', string='Our Reference', index=True, track_visibility='onchange')


	@api.multi
	def create(self, vals):
		res = super(sale_order, self).create(vals)
		if vals.get('opportunity_id'):
			res.write({'user_id':self.env['crm.lead'].browse(vals.get('opportunity_id')).user_id.id})
		else:
			if vals.get('partner_id'):
				res.write({'user_id':self.env['res.partner'].browse(vals.get('partner_id')).user_id.id})
		return res


	@api.multi
	@api.onchange('opportunity_id')
	def onchange_opportunity_id(self):
		res = {'value':{}}
		order_lines = []
		if self.opportunity_id and self.opportunity_id.lead_line_ids:
			for op_line in self.opportunity_id.lead_line_ids:
				taxlist = []
				for itax in op_line.tax_id:
					taxlist.append(itax.id)
				line_dict = {
					'product_id':op_line.product_en,
					'product_uom_qty':op_line.qty_en,
					'part_number':op_line.part_number.id,
					'part_number_product':op_line.part_number_product.id,
					'drawing_number':op_line.internal_code_en,
					'workpiece_grade':op_line.workpiece_grade.id,
					'kind_of_machine':op_line.kind_of_machine.id,
					'workpiece_material':op_line.workpiece_material.id,
					'coating_en':op_line.coating_en.id,
					'price_unit':op_line.unit_price_en,
					'pricing_date':op_line.pricing_date,
					'part_name':op_line.part_name,
					'add_name_1':op_line.add_name_1,
					'add_name_2':op_line.add_name_2,
					'name':op_line.remarks_en,
					'partner_id':op_line.partner_id.id,
					'discount':op_line.discount,
					'stat_line':'open',
					'tax_id':[(6,0,taxlist)],
					'product_uom':op_line.product_uom,
					'currency_id':op_line.currency_id,
				}
				order_lines.append((0, 0, line_dict))
				self.order_line = order_lines
				self.contact_id = self.opportunity_id.our_reference_ids.id,
		# return res

	@api.multi
	def action_confirm(self):
		for order in self:
			print "###########",self , self._context
			new_order  = ''
			num_of_line = 0
			line_list = []
			for line in order.order_line:
				if line.confirm_line_box == True and line.stat_line == 'open':
					taxlist = []
					for itax in line.tax_id:
						taxlist.append(itax.id)
					line_list.append((0, 0, {
						'product_id': line.product_id.id,
						'product_uom_qty': line.product_uom_qty,
						'price_unit':line.price_unit,
						'discount': line.discount,
						'name':line.name,
						'po_num':self._context.get('po_num'),
						'part_number':line.part_number.id,
						'part_number_product':line.part_number_product.id,
						'drawing_number':line.drawing_number,
						'workpiece_grade':line.workpiece_grade.id,
						'kind_of_machine':line.kind_of_machine.id,
						'workpiece_material':line.workpiece_material.id,
						'coating_en':line.coating_en.id,
						'pricing_date':line.pricing_date,
						'part_name':line.part_name,
						'add_name_1':line.add_name_1,
						'add_name_2':line.add_name_2,
						'partner_id':line.partner_id.id,
						'stat_line':'so',
						'confirm_line_box':True,
						'layout_category_id':line.layout_category_id.id,
						'product_uom':line.product_uom.id,
						'customer_lead':line.customer_lead,
						'tax_id':[(6,0,taxlist)],
					}))
					line.write({'stat_line':'so'})
			for line in order.order_line:
				if line.stat_line == 'so':
					num_of_line += 1

			if order.tag_ids:
				tag_list = order.tag_ids.ids
			else:
				tag_list = []

			if line_list:
				order_name = self.search_count([('or_sale_id','=',order.id)])
				if order_name == 0:
					order_name = 1
				else:
					order_name += 1
				sale_dict = {
					'name':order.name + '/SO' + str(order_name),
					'sale_order_name_id':order.sale_order_name_id.id,
					'partner_id':order.partner_id.id,
					'date_order':order.date_order,  
					'pricelist_id':order.pricelist_id.id,
					'user_id':order.user_id.id,
					'picking_policy':order.picking_policy,
					'opportunity_id':order.opportunity_id.id,
					'warehouse_id':order.warehouse_id.id,
					'team_id':order.team_id.id,
					'po_num':self._context.get('po_num'),
					'order_date':self._context.get('order_date'),
					'or_sale_id':order.id,
					'revision':order.revision,
					'goods_label':order.goods_label,
					'carrier_id':order.carrier_id.id,
					'payment_term_id':order.payment_term_id.id,
					'hide_confirm':True,
					'order_line':line_list,
					'incoterm':order.incoterm.id,
					'delivery_term_id':order.delivery_term_id.id,
					'delivery_time_id':order.delivery_time_id.id,
					'tag_ids': [(6,0, tag_list)],
					'contact_id':order.contact_id.id,
					'related_project_id':order.related_project_id.id,
					'origin':order.origin,
					'campaign_id':order.campaign_id.id,
					'medium_id':order.medium_id.id,
					'source_id':order.source_id.id,
					'opportunity_id':order.opportunity_id.id,
					'transport_payer':order.transport_payer,
					'buyer_comment':order.buyer_comment,
					'customer_transport_time_days':order.customer_transport_time_days,
					'customer_invoice_code':order.customer_invoice_code,
					'buyer_reference':order.buyer_reference,
				}
				new_order = self.env['sale.order'].create(sale_dict)
				new_order.state = 'sale'
				new_order.confirmation_date = fields.Datetime.now()
				new_order.order_line._action_procurement_create()
				# if self.env.context.get('send_email'):
				# 	new_order.force_quotation_send()
		
				if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
					new_order.action_done()
				new_order.state = 'sale'
			if len(order.order_line) != 0:
				if num_of_line == len(order.order_line):
					order.write({'hide_confirm':True})
			if line_list:
				return new_order
			else:
				raise UserError(_('Please Select Order Line Before Confirm Order.'))
		return True

class sale_order_line(models.Model):
	_inherit= 'sale.order.line'

	@api.model
	def _get_partner(self):
		partner = False
		context = self._context or {}
		if context.get('partner_id'):
			partner = context.get('partner_id')
		return partner


	part_number = fields.Many2one('sequence.number.partner','Price History')
	part_number_product = fields.Many2one('sequence.number.product','Part Number')
	drawing_number = fields.Char('Drawing Number')
	workpiece_grade = fields.Many2one('workpiece.grade','Workpiece Grade')
	kind_of_machine = fields.Many2one('kind.of.machine','Kind of Machine')
	workpiece_material = fields.Many2one('workpiece.material','Workpiece Material')
	coating_en = fields.Many2one('coating.enquiry','Coating')
	pricing_date = fields.Date('Pricing Date')
	name = fields.Text(string='Remarks',required=False)
	partner_id = fields.Many2one('res.partner',string='Account' ,default=_get_partner,store=True)

	confirm_line_box = fields.Boolean('.')
	stat_line = fields.Selection([('so','SO'),('open','Open')],'Status',default='open')
	check_uid = fields.Boolean(compute='compute_vissibility', string='Users')
	add_name_1 = fields.Char('Add Name 1')
	add_name_2 = fields.Char('Add Name 2')
	part_name = fields.Char('Part Name')

	@api.multi
	def create(self, vals):
		if not vals.get('name'):
			vals.update({'name':self.env['product.product'].browse(vals.get('product_id')).name})
		return super(sale_order_line, self).create(vals)

	@api.multi
	@api.onchange('product_uom_qty')
	def on_changeunit_qty(self):
		if self.part_number:
			self.price_unit = self.part_number.seq_price

	@api.multi
	@api.onchange('price_unit')
	def on_changeunit_price_en(self):
		for ob in self:
			self.pricing_date = fields.Datetime.now()

	@api.multi
	@api.onchange('part_number')
	def part_number_change(self):
		for part in self:
			values = {
				'price_unit': part.part_number.seq_price,
				'pricing_date': part.part_number.pricing_date,
			}
		self.update(values)

	@api.multi
	@api.onchange('part_number_product')
	def part_number_product_change(self):
		for part in self:
			self.drawing_number = part.part_number_product.drawing_number
			vals = {}
		if part:
			vals['workpiece_grade'] = self.part_number_product.workpiece_grade.id
			vals['kind_of_machine'] = self.part_number_product.kind_of_machine.id
			vals['coating_en'] = self.part_number_product.coating_en.id
			vals['workpiece_material'] = self.part_number_product.workpiece_material.id
			vals['drawing_number'] = self.part_number_product.drawing_number
			vals['add_name_1'] = self.part_number_product.add_name_1
			vals['add_name_2'] = self.part_number_product.add_name_2
			vals['price_unit'] = self.part_number_product.lst_price
		self.update(vals)

	@api.one	
	@api.depends('price_unit')
	def compute_vissibility(self):
		if self.env.user.technical_support_b == True or self.env.user.sales_person_b == True or self.env.user.sales_supervisor_b == True or self.env.user.sales_coordinator_b == True:
			self.check_uid = True

