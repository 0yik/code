# -*- coding: utf-8 -*-

from odoo import models, fields, api

class minimum_maximum_sales_discount(models.Model):
	_name = 'minimum.maximum.sales.discount'

	line_id = fields.Many2one('pos.promotion','Promotion')
	first_min_qty = fields.Integer('Frist Item Min Qty')
	second_max_qty = fields.Integer('Second Item Max Qty')
	first_minimum_sales = fields.Integer('Min Sales First Item')
	discount_amount = fields.Integer('Discount % Second Item')

class minimum_sales_discount(models.Model):
	_name = 'minimum.sales.discount'

	line_id = fields.Many2one('pos.promotion','Promotion')
	minimum_sales = fields.Integer('Minimum Sales')
	discount_amount = fields.Integer('Discount Amount')
	type = fields.Selection([
	    ('1_discount_total_order', 'Discount on total order'),
	    ('2_discount_category', 'Discount on categories'),
	    ('3_discount_by_quantity_of_product', 'Discount by quantity of product'),
	    ('4_pack_discount', 'By pack products discount products'),
	    ('5_pack_free_gift', 'By pack products free products'),
	    ('6_price_filter_quantity', 'Price product filter by quantity'),
	    ('7_discount_amount_with_sales','Discount Amount with Minimum Sales'),
	    ('8_global_disc_with_payment_type','Global Disc% with payment type'),
	    ('9_second_item_disc_with_min_max_qty','Second item Disc% with Min Max Qty')
	], 'Type',related='line_id.type',store=True)
	payment_method_id = fields.Many2one('account.journal','Payment Method')

class import_pos_promotion_product(models.Model):
	_name = 'import.pos.promotion.product'

	line_id = fields.Many2one('pos.promotion','Promotion')
	product_code = fields.Char('Product Code')
	product_id = fields.Many2one('product.product','Product')
	product_code2 = fields.Char('Product Code2')
	product_id2 = fields.Many2one('product.product','Product2')
	categ_id = fields.Many2one('pos.category','POS Category')
	sale_price = fields.Float('Sale Price')
	discount_exception = fields.Integer('Discount %')
	item_type = fields.Selection([('all item no exception','All Item No Exception'),
										('all item with exception','All Item With Exception'),
										('must include specific item','Must Include Specific Item'),
										('specific item only','Specific Item Only')
										], string='Item Type' ,related='line_id.item_type',store=True)
 
class program_branch(models.Model):
	_inherit='pos.promotion'

	period_type = fields.Selection([('all_time','All Time Discount'),('birthday','Birthday Discount'),('certain_time','Certain Time Discount')], string='Period Type')
	item_type = fields.Selection([('all item no exception','All Item No Exception'),
										('all item with exception','All Item With Exception'),
										('must include specific item','Must Include Specific Item'),
										('specific item only','Specific Item Only')
										], string='Item Type', help='1. All item No Exception : Promo will apply to all item without exception, you don`t have to enter any item.\n 2.All item with Exception : Promo will apply to all item except item listed here, please select exceptional item from the list. \n 3.Must Include Specific Item : Promo will apply if included specific item listed here, please select functional from list. \n 4.Specific Item Only : Promo will apply only to specific item listed here, please select functional item from the list')
	buyer_type = fields.Selection([('all_buyer','All Buyer'),('member_only','Member Only'),('non_member','Non Member')],string='Buyer Type')
	type = fields.Selection([
	    ('1_discount_total_order', 'Discount on total order'),
	    ('2_discount_category', 'Discount on categories'),
	    ('3_discount_by_quantity_of_product', 'Discount by quantity of product'),
	    ('4_pack_discount', 'By pack products discount products'),
	    ('5_pack_free_gift', 'By pack products free products'),
	    ('6_price_filter_quantity', 'Price product filter by quantity'),
	    ('7_discount_amount_with_sales','Discount Amount with Minimum Sales'),
	    ('8_global_disc_with_payment_type','Global Disc% with payment type'),
	    ('9_second_item_disc_with_min_max_qty','Second item Disc% with Min Max Qty')
	], 'Type', required=1)
	import_line_ids = fields.One2many('import.pos.promotion.product','line_id',string='Import Product')
	minimum_sales_ids = fields.One2many('minimum.sales.discount','line_id',string="Minimum Sales")
	min_max_sales_ids = fields.One2many('minimum.maximum.sales.discount','line_id',string="Minimum Maximum Sales")