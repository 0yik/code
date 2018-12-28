# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class sales_promotion_code(models.Model):
    _name = 'sales.promotion.code'
    _rec_name = 'name'

    name = fields.Char(string='Promotional Code')
    qty_of_photos = fields.Integer('Quantity of Photos')
    discount = fields.Float(string='Discount(%)')
    quantity = fields.Float('Quantity', digits=dp.get_precision('Product UoS'))
    discount_fixed = fields.Float(string='Discount($)')
    product_id = fields.Many2many('product.product', string='Product')
    product_categ_id = fields.Many2many('product.category', string='Product Category')
    date_start = fields.Datetime(string='Start Date & Time')
    date_end = fields.Datetime(string='End Date & Time')
    comment = fields.Text(string='Description')
    note = fields.Text('Remarks')

    _sql_constraints = [('promotion_code_unique', 'unique(name)', 'This promotion code already available..!')]
