# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT



class CustomProductPack(models.Model):
	_inherit = "purchase.order.line"

	pack_barcode = fields.Char(related='product_id.barcode', string='Package Barcode')

class CustomProductPackField(models.Model):
	_inherit = "purchase.order"

	pack_barcode = fields.Char( string='Package Barcode')

	
