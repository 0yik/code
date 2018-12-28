# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.template'

    rent_disc_available = fields.Boolean("Discount Available")
    rent_disc = fields.Integer("Discount")
    rent_disc_price = fields.Float(compute="_compute_rent_disc_price", string="Final Price", store=True)

    @api.depends('rent_disc_available', 'rent_disc')
    def _compute_rent_disc_price(self):
        for product in self:
            product.rent_disc_price = product.rent_price - ((product.rent_price * product.rent_disc) / 100)
