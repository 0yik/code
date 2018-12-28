# -*- coding: utf-8 -*-

from odoo import api, fields, models


class product_template(models.Model):
    _inherit = 'product.template'

    @api.multi
    def dummy_inverse(self):
        """
        Dummy Inverse function so that we can edit vouchers and save changes
        """
        return True

    @api.multi
    def get_location_ids(self):
        for product_id in self:
            product_id.location_ids = product_id.location_ids.search([('usage', '=', 'internal')])

    location_ids = fields.One2many(
        'stock.location',
        compute='get_location_ids',
        inverse='dummy_inverse',
        string='Locations',
    )
