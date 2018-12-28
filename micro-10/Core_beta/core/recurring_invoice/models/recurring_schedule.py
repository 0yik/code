# -*- coding: utf-8 -*-

from odoo import models, fields, api

class recurring_schedule(models.Model):
    _name = 'recurring.schedule'

    date = fields.Date(required=True,string='Date')
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    invoice_state = fields.Selection(related="invoice_id.state",string='Invoice State')
    invoice_number = fields.Char(related="invoice_id.number",string='Invoice Number')
    recurring_invoice_id = fields.Many2one('recurring.invoice',string='Recuring invoice')
    created = fields.Boolean('Created',default=False)
    is_last = fields.Boolean('Is last schedule on recurring')


