# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def pay_invoice_using_paypal(self):
        self.ensure_one()
        self.sudo().action_invoice_open()
        return {
            'type': 'ir.actions.act_url',
            'name': "Paypal Invoice",
            'target': 'self',
            'url': '/invoice/payment?invoice_id='+str(self.id), 
        }
