# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from openerp.exceptions import Warning, ValidationError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    booking_order_id = fields.Many2one('booking.order',string="Booking Order")
    