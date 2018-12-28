# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    partner_delivery_address_id = fields.Many2one('delivery.address', string='Delivery Address', required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current customer invoice.")
