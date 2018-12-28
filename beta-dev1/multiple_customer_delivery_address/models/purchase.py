# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_invoice(models.Model):
    _inherit = 'purchase.order'

    partner_delivery_address_id = fields.Many2one('delivery.address', string='Delivery Address', required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current customer invoice.")

