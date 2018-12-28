# -*- coding: utf-8 -*-

import base64
import urllib2

import boto3
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class Custom_Procurement_Order(models.Model):
    _inherit = 'procurement.order'

    supplier_id = fields.Many2one('res.partner', 'Supplier Id')
    sqs_product_id = fields.Char(string='Product Id', help='Product Id.')
    sqs_supplier_id = fields.Char(string='Supplier Id', help='Supplier Id.')

    def _get_stock_move_values(self):
		vals = super(Custom_Procurement_Order, self)._get_stock_move_values()
		vals['supplier_id'] = self.supplier_id.id
		vals['sqs_product_id'] = self.sqs_product_id
		vals['sqs_supplier_id'] = self.sqs_supplier_id
		return vals