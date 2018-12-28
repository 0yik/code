# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

class Invoice(models.Model):
    _inherit = 'account.invoice'
    
    collect_sign = fields.Binary(string='Collect Signature') 
    return_sign = fields.Binary(string='Return Signature')
    recv_ref_depo = fields.Boolean(string='Received Refundable Deposit')
