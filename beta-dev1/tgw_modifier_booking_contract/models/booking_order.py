# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime,time
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning, ValidationError

class BookingOrderLine(models.Model):
    _inherit = 'booking.order.line'
    
    serial_no = fields.Char(string='Product’s Serial No.', required=False)
    barcode = fields.Char(string='Barcode', related="product_id.barcode",required=False)