# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_customer_display = fields.Boolean(string='Allow Customer Display',default="True")
    customer_display_ip = fields.Char(string="Customer display IP address",default="http://0.0.0.0:8100")
    customer_display_next_l1 = fields.Char(string="Next Customer (top line)", default="Welcome")
    customer_display_next_l2 = fields.Char(string="Next Customer (bottom line)", default="Point of Sale Open")
    customer_display_closed_l1 = fields.Char(string="POS Closed (top line)", default="Point of Sale Closed")
    customer_display_closed_l2 = fields.Char(string="POS Closed (bottom line)", default="See you soon!")


