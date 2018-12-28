# -*- coding: utf-8 -*-

from openerp import models, fields


class Custom_Shipping_Address(models.Model):
    _name = 'shipping.address'

    name = fields.Char()
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict')
    phone = fields.Char()
    shipping_code = fields.Char()
    shipping_method = fields.Char()


class Custom_Billing_Address(models.Model):
    _name = 'billing.address'

    name = fields.Char()
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict')
    phone = fields.Char()
