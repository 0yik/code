# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from odoo.exceptions import UserError, ValidationError

class arkco_modifier_crm_lead(models.Model):
	_inherit = 'crm.lead'

	date_created = fields.Datetime(string="Date Created",default=datetime.datetime.today())
	date_deadline = fields.Date(string="Expected Closing",compute="change_expiry_date")
	product_interested = fields.Many2one('product.product',string="Product Interested")
	location = fields.Many2one('stock.location',string="Location", domain="[('usage', '=', 'internal')]") 
	total_nup_list = fields.Integer(string="Total NUP List",default="0")
	name = fields.Char(required=True, index=True, default="New")
	crm_title = fields.Text()
	is_true = fields.Boolean(default=False)

	nup_price = fields.Float(compute="get_product_price")
	number = fields.Integer(compute="get_nup_number")

	# @api.onchange('waiting_id')
	# def get_total_nup_list(self):
	# 	self.total_nup_list = len(self.waiting_id.ids)

	@api.depends('product_interested')
	def get_product_price(self):
		for rec in self:
			rec.nup_price = rec.product_interested.nup_price

	@api.multi
	@api.onchange('product_interested','location')
	def get_waiting_list(self):
		if self.product_interested and self.location:
			waiting_ids_list = []
			ids = self.search([('product_interested','=',self.product_interested.id),('location','=',self.location.id)])
			for line in ids:
				if self != line:
					deposit_id = self.env['account.payment'].search([('name_sequence','=',line.name),('state','=','posted')])
					if deposit_id:
						rec={
						'number':len(waiting_ids_list)+1,
						'nup_number':line.name,
						'nup_payment_date':deposit_id.payment_date,
						'customer':line.partner_id.id,
						'sales_executive':line.user_id.id
						}
						waiting_ids_list.append([0,0,rec])
			if waiting_ids_list:
				self.waiting_id = waiting_ids_list
			self.update({'total_nup_list':len(waiting_ids_list)})

	@api.model
	def create(self,values):
		values['crm_title'] = values['name']
		res = super(arkco_modifier_crm_lead,self).create(values)
		name = self.env['ir.sequence'].next_by_code('crm.lead')
		date = datetime.datetime.today().strftime('%d%m%y')
		prefix = 'NUP|'+date+'|'
		name = name.replace('NUP',prefix)
		res.crm_title = res.name
		res.name = name
		res.update({'is_true':True,'total_nup_list':len(res.waiting_id)})

		# It will check the waiting after creation of lead
		# ids = self.search([('product_interested','=',res.product_interested.id),('location','=',res.location.id)])
		# for line in ids:
		# 	if res != line:
		# 		deposit_id = self.env['account.payment'].search([('name_sequence','=',line.name),('state','=','posted')])
		# 		if deposit_id:
		# 			rec={
		# 			'number':len(res.waiting_id)+1,
		# 			'nup_number':line.name,
		# 			'nup_payment_date':deposit_id.payment_date,
		# 			'customer':line.partner_id.id,
		# 			'sales_executive':line.user_id.id
		# 			}
		# 			res.write({'waiting_id':[(0,0,rec)]})
		# 			# res.product_interested.unit_status = 'reserved'	
		# res.total_nup_list = len(res.waiting_id.ids)
		return res

	def get_nup_number(self):
		for rec in self:
			ids = self.env['account.payment'].search([('partner_id','=',self.partner_id.id),('name_sequence','like',self.name),('state','=','posted')]).ids
			self.number = len(ids)
	
	@api.multi
	def get_button_nup(self):
		return {
		'name': ('Customer Deposit'),
		'view_type': 'form',
		'view_mode': 'tree,form',
		'res_model': 'account.payment',
		'view_id': False,
		'type': 'ir.actions.act_window',
		'domain': [('partner_id', '=', self.partner_id.id),('name_sequence','like',self.name),('state','=','posted')],
		}

	@api.depends('date_created')
	def change_expiry_date(self):
		for rec in self:
			rec.date_deadline = str(datetime.datetime.strptime(rec.date_created, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=2)) 

	waiting_id = fields.One2many('waiting.list','crm_id') 

	@api.multi
	def print_crm_lead(self):
		deposit_id = self.env['account.payment'].search([('name_sequence','=',self.name)])
		if deposit_id:
			res = self.env['report'].get_action(self,'arkco_modifier_crm_lead.crm_lead_report')
		else:
			raise ValidationError('Customer is not having NUP Deposit....!')

		return res

class waiting_list(models.Model):
	_name = 'waiting.list'

	number = fields.Integer(string="NO")
	nup_number = fields.Char(string="NUP Number")
	customer = fields.Many2one('res.partner',string="Customer")
	nup_payment_date = fields.Date(string="NUP Payment Date")
	sales_executive = fields.Many2one('res.users',string="Sales Executive")
	is_partner = fields.Boolean(default=False)

	crm_id = fields.Many2one('crm.lead',string="Waiting List",oncascade="delete",index=True)

class waiting_list_account(models.Model):
	_inherit = 'account.payment'

	name_sequence = fields.Char()

	@api.onchange('amount')
	def onchnage_remaining_amount(self):
		if self.state == "posted":
			self.remaining_amount = self.amount

	@api.model
	def create(self, vals):
		if vals.get('amount'):
			vals.update({'remaining_amount': 0.0})
		res = super(waiting_list_account, self).create(vals)
		if res.state == "draft":
			res.remaining_amount = 0.00
		return res

	@api.multi
	def post(self):
		res = super(waiting_list_account,self).post()
		self.remaining_amount = self.amount
		if self.name_sequence:
			self.name = 'NUP IN/'+self.name_sequence
			waiting_list = self.env['crm.lead'].search([('name','=',self.name_sequence)])
			user_id = self.env['crm.lead'].search([('name','=',self.name_sequence)]).user_id

			res = {
				'number':len(waiting_list.waiting_id.ids)+1,
				'nup_number':self.name_sequence,
				# 'nup_price':self.amount,
				'nup_payment_date':self.payment_date,
				'sales_executive': user_id.id,
				'customer': self.partner_id.id,
				'is_partner':True
				}

			hat="reserved"
			waiting_list.product_interested.unit_status = hat
			waiting_list.write({'waiting_id':[(0,0,res)],'total_nup_list':waiting_list.total_nup_list+1})
			waiting_list.total_nup_list = len(waiting_list.waiting_id.ids)
			waiting_list.stage_id = waiting_list.stage_id.search([('name','ilike','Hot')])