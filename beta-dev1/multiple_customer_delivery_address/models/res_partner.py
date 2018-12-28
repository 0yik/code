# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    delivery_address_ids = fields.One2many('delivery.address', 'partner_id', string='Delivery Address',)
