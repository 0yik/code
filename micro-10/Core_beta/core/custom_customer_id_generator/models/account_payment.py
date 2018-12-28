# -*- coding: utf-8 -*-
from odoo import api, fields, models

class account_payment(models.Model):
    _inherit = 'account.payment'
    
    customer_id = fields.Char('Customer Id', related='partner_id.customer_id', store=True)
