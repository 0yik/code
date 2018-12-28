# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime

class sale_order(models.Model):
	_inherit = 'sale.order'
	revision = fields.Char('Revision')
	goods_label = fields.Char('Goods Label')
	sale_order_name_id = fields.Many2one('sale.order.name','Quote Name')
	delivery_term_id = fields.Many2one('delivery.term','Delivery Term')
	delivery_time = fields.Date('Delivery Time')
	manual_sequence = fields.Char('Quote Number')
	contact_id = fields.Many2one('res.partner','Our Reference')
	
	def get_date_order(self,order_date):
		if order_date:
			date_str = str(order_date).split(' ')
			date_str_split = str(date_str[0]).split('-')
			date = date_str_split[1] +'/'+date_str_split[2]+'/'+date_str_split[0]
			return date
		else:
			return ' '
	
	def get_printout_date(self):
		currentDT = datetime.datetime.now()
		date = currentDT.strftime("%m/%d/%Y")
		return date
	
	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('sale.quotation.intipresisi') or 'New'
		sale_order_obj = super(sale_order, self).create(vals)
		name = sale_order_obj.name
		latest_name = name.replace('XXX',sale_order_obj.partner_id.short_name)
		sale_order_obj.write({'name':latest_name})
		return sale_order_obj
	


class sale_order_name(models.Model):
	_name = 'sale.order.name'
	name = fields.Char('Name',required=True)
	
class delivery_term(models.Model):
	_name = 'delivery.term'
	name = fields.Char('Name',required=True)
