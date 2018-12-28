# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields,models
from odoo.exceptions import UserError, Warning, ValidationError, RedirectWarning
import string, math, random, re
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from reportlab.graphics.barcode import createBarcodeDrawing

def ean_checksum(eancode):
	"""returns the checksum of an ean string of length 13, returns -1 if the string has the wrong length"""
	if len(eancode) != 13:
		return -1
	oddsum=0
	evensum=0
	total=0
	eanvalue=eancode
	reversevalue = eanvalue[::-1]
	finalean=reversevalue[1:]

	for i in range(len(finalean)):
		if i % 2 == 0:
			oddsum += int(finalean[i])
		else:
			evensum += int(finalean[i])
	total=(oddsum * 3) + evensum

	check = int(10 - math.ceil(total % 10.0)) %10
	return check

def check_ean(eancode):
	"""returns True if eancode is a valid ean13 string, or null"""
	if not eancode:
		return True
	if len(eancode) != 13:
		return False
	try:
		int(eancode)
	except:
		return False
	return ean_checksum(eancode) == int(eancode[-1])

def sanitize_ean13(ean13):
	"""Creates and returns a valid ean13 from an invalid one"""
	if not ean13:
		return "0000000000000"
	ean13 = re.sub("[A-Za-z]","0",ean13)
	ean13 = re.sub("[^0-9]","",ean13)
	ean13 = ean13[:13]
	if len(ean13) < 13:
		ean13 = ean13 + '0' * (13-len(ean13))
	return ean13[:-1] + str(ean_checksum(ean13))


def _code_generator(size=13, chars=string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

class MembershipConfig(models.Model):
	_name = 'membership.config'

	@api.model
	def process_expiry_check_scheduler(self):
		expired_cards_objs = self.env['pos.membership.card'].search([]).filtered(lambda card:datetime.strptime(card.expiry_date,DEFAULT_SERVER_DATETIME_FORMAT) < datetime.strptime(fields.Datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT) and card.state == 'confirm')
		expired_cards_objs.write({'state':'expired'})


class PosConfig(models.Model):
	_inherit = 'pos.config'
	override_existing_discount = fields.Boolean('Override Existing Discount If Exists', compute="_get_config_settings")
	ignore_membership_discount = fields.Boolean('Ignore Membership Discount If Discount Already Exists', compute="_get_config_settings")
	override_selection = fields.Char(compute="_get_config_settings")
	ignore_selection = fields.Char(compute="_get_config_settings")

	def _get_config_settings(self):
		ir_value_obj = self.env['ir.values']
		pos_setting_values = ir_value_obj.sudo().get_defaults('pos.config.settings')
		pos_config_settings = {i[1]: i[2] for i in pos_setting_values}
		if len(pos_config_settings) == 0:
			pos_config_settings = {'ignore_selection': 'all_membership_discounts', 'ignore_membership_discount': False, 'override_existing_discount': False, 'override_selection': 'all_existing_discounts', 'allow_one_card_per_customer': False}
		for obj in self:
			obj.override_existing_discount = pos_config_settings['override_existing_discount']
			obj.ignore_membership_discount = pos_config_settings['ignore_membership_discount']
			obj.override_selection = pos_config_settings['override_selection']
			obj.ignore_selection = pos_config_settings['ignore_selection']

class PosConfigSettings(models.TransientModel):
	_inherit = 'pos.config.settings'

	override_existing_discount = fields.Boolean('Override Existing Discount If Exists')
	ignore_membership_discount = fields.Boolean('Ignore Membership Discount If Discount Already Exists')
	override_selection = fields.Selection([
		("all_existing_discounts","Override all existing discounts."),
		("only_less_discounts","Override existing discounts which are less than membership discounts.")])
	ignore_selection = fields.Selection([
		("all_membership_discounts","Ignore membership discounts for all orderlines."),
		("only_where_discounts_exists","Ignore membership discounts for only those orderlines where discount exists.")])
	allow_one_card_per_customer = fields.Boolean('Membership Cards')

	@api.onchange('override_existing_discount')
	def onchange_override_existing_discount(self):
		if self.override_existing_discount:
			self.ignore_membership_discount = False
			self.override_selection = 'all_existing_discounts'

	@api.onchange('ignore_membership_discount')
	def onchange_ignore_membership_discount(self):
		if self.ignore_membership_discount:
			self.override_existing_discount = False
			self.ignore_selection = 'all_membership_discounts'

	@api.multi
	def set_wk_fields(self):
		ir_values_obj = self.env['ir.values']
		ir_values_obj.sudo().set_default('pos.config.settings', "override_existing_discount", self.override_existing_discount)
		ir_values_obj.sudo().set_default('pos.config.settings', "ignore_membership_discount", self.ignore_membership_discount)
		ir_values_obj.sudo().set_default('pos.config.settings', "override_selection", self.override_selection)
		ir_values_obj.sudo().set_default('pos.config.settings', "ignore_selection", self.ignore_selection)
		ir_values_obj.sudo().set_default('pos.config.settings', "allow_one_card_per_customer", self.allow_one_card_per_customer)
	

	@api.multi
	def get_default_wk_fields(self, fields):
		ir_value_obj = self.env['ir.values']
		pos_setting_values = ir_value_obj.sudo().get_defaults('pos.config.settings')
		pos_config_settings = {i[1]: i[2] for i in pos_setting_values}
		return pos_config_settings


class PosMembershipCategory(models.Model):
	_name = 'pos.membership.category'

	name = fields.Char("Name", required=True)
	discount = fields.Float("Discount (%)", required=True)
	max_validity = fields.Integer('Default Validity Period (In Years)', required=True, help="Default validity period only for unexpired cards.")
	
	@api.constrains('discount')
	def discount_validation(self):
		if self.discount <= 0:
			raise ValidationError("Discount should be greater than zero!!!")
		elif self.discount > 100:
			raise ValidationError("Discount cannot be greater than 100!!!")

	@api.constrains('max_validity')
	def max_validity_validation(self):
		if self.max_validity <= 0:
			raise ValidationError("Default validity period should be greater than zero!!!")


class PosMembershipCard(models.Model):
	_name = 'pos.membership.card'
	name = fields.Char("Name", related = "card_category.name")

	def generate_ean13(self,code):
		return sanitize_ean13(code)
	
	def _compute_validity_in_days(self):
		current_date = datetime.strptime(fields.Datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
		expiry_date = datetime.strptime(self.expiry_date, DEFAULT_SERVER_DATETIME_FORMAT)
		self.validity = (expiry_date - current_date).days + 1

	@api.one
	def _compute_expiry_date(self):
		issue_date = datetime.strptime(self.issue_date, DEFAULT_SERVER_DATETIME_FORMAT)
		self.expiry_date = issue_date.replace(year = issue_date.year + self.card_category.max_validity)		

	@api.onchange('validity','state')
	def onchange_validity(self):	
		if self.validity and self.validity <= 0:
			self.state = 'expired'

	@api.onchange('card_category')
	def onchange_card_category(self):	
		if self.card_category:
			issue_date = datetime.strptime(self.issue_date, DEFAULT_SERVER_DATETIME_FORMAT)
			self.expiry_date = issue_date.replace(year = issue_date.year + self.card_category.max_validity)		

	@api.constrains('card_code')
	def unique_code_validation(self):
		membership_card_ids = self.search([('card_code','=',self.card_code),('state','=','confirm')])
		if membership_card_ids.ids:
			raise ValidationError('This barcode is already assign to some other membership card.Please generate another bar code.')

	user_id =fields.Many2one('res.users',string='User Name',required=True, default= lambda self: self.env.user, invisible=True )
	card_category = fields.Many2one("pos.membership.category",string="Membership Template", required=True)
	customer_id =  fields.Many2one('res.partner', 'Customer', required=True, domain=[('customer','=',True)])
	expiry_date = fields.Datetime(string='Expiry Date')
	validity = fields.Integer(compute="_compute_validity_in_days",string='Validity(in days)', readonly=1)
	issue_date = fields.Datetime('Issue Date', default=fields.Datetime.now)
	state = fields.Selection([
		("draft","Draft"),
		("confirm","Confirm"),
		("expired","Expired"),
		("cancel","Cancel")], default = 'draft')
	card_code = fields.Char("Card Code")

	@api.one
	def card_confirm(self):
		ir_value_obj = self.env['ir.values']
		pos_setting_values = ir_value_obj.sudo().get_defaults('pos.config.settings')
		pos_config_settings = {i[1]: i[2] for i in pos_setting_values}
		allow_one_card_per_customer = pos_config_settings.get('allow_one_card_per_customer')
		if allow_one_card_per_customer:
			existimg_card_ids = self.env['pos.membership.card'].search([('customer_id','=',self.customer_id.id),('state','=','confirm')]).ids
			if len(existimg_card_ids) > 0:
				raise UserError("You have already assigned a membership card to the selected customer!!!")
		if self.card_code == False:
			raise UserError("Please enter a card code !!!")
		else:
			existimg_card_ids = self.env['pos.membership.card'].search([('card_code','=',self.card_code),('state','=','confirm')]).ids
			if len(existimg_card_ids) > 0:
				raise UserError("Please use some other card code !!!\nThis code has already been used for some other card.")
			else:
				self.state = 'confirm'

	@api.one
	def card_cancel(self):
		self.state = 'cancel'

	@api.one
	def generate_code(self):
		self.card_code = self._generate_code()

	def _generate_code(self):
		while True:
			code = _code_generator()
			check = self.search([('card_code', '=', code)])
			if not check:
				break
		return self.generate_ean13(code)

	@api.model
	def get_card_details(self,kwargs):
		result={}
		card_obj = self.env['pos.membership.card'].search([('card_code','=',kwargs['card_code']),('state','in',['confirm','expired'])])
		if len(card_obj)>1:
			result['status'] = False
			result['message'] = 'Unknown Error. Contact your moderator'
		elif len(card_obj)==0:
			result['status'] = False
			result['message'] = 'Card does not exist !!!'
		else:
			if datetime.strptime(card_obj.expiry_date, DEFAULT_SERVER_DATETIME_FORMAT) < datetime.strptime(fields.Datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT) or card_obj.state =='expired':
				result['status'] = False
				result['message'] = ('This card has expired on (%s) !!!')%card_obj.expiry_date
			else:
				result['status'] = True
				result['card_category'] = card_obj.card_category.name
				result['customer_name'] = card_obj.customer_id.name
				result['customer_id'] = card_obj.customer_id.id
				result['expiry_date'] = card_obj.expiry_date
				result['discount'] = card_obj.card_category.discount
		return result

	@api.model
	def confirm_demo_membership_card(self):
		membership_card_objs = self.search([])
		if membership_card_objs:
			membership_card_obj = membership_card_objs[0]
			membership_card_obj.generate_code()
			membership_card_obj._compute_expiry_date()
			membership_card_obj.card_confirm()