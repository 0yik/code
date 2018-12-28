# -*- coding: utf-8 -*-

from odoo import models, fields, api

class shop_type(models.Model):
	_name = 'shop.type'
	name = fields.Char(string="Name")



class city_city(models.Model):
	_name = 'city.city'
	name =  fields.Char(string="Name")


class res_branch(models.Model):
	_inherit='res.branch'

	country_code = fields.Char(string="Counter code", size=12)
	reg_key = fields.Char(string="Registration Key")
	customer_care = fields.Many2one('hr.employee', string="Customer Care")
	city = fields.Many2one('city.city',string="City")
	shoptype_id =  fields.Many2one('shop.type', string="Shop Type")
	size_counter = fields.Char(string="Size Counter")
	category_mall = fields.Selection(
		selection=[('a', 'A'),
					('b', 'B'),('c', 'C')],
		string='Category Mall',
		default='a',
	)
	location  = fields.Char(string="Location")
	email = fields.Char(string="Email")
	pic_id = fields.Many2one('hr.employee',string="PIC")
	description =  fields.Char(string="Description")
	open_date =  fields.Date(string="Open Date")
	close_date = fields.Date(string="Close Date")
	active  = fields.Boolean(default=True)
	is_warehouse = fields.Boolean('Is A Warehouse', default=True)


class Saleorder(models.Model):
	_inherit = 'sale.order'

	branch_id = fields.Many2one('res.branch', 'Branch', required=False)


class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	branch_id = fields.Many2one('res.branch', 'Branch', required=False)