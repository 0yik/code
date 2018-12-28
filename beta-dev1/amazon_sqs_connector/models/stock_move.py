# -*- coding: utf-8 -*-

import base64
import urllib2
import boto3
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class Custom_Stock_Move(models.Model):
    _inherit = 'stock.move'

    supplier_id = fields.Many2one('res.partner', 'Supplier')
    sqs_product_id = fields.Char(string='Product Id', help='Product Id.')
    sqs_supplier_id = fields.Char(string='Supplier Id', help='Supplier Id.')