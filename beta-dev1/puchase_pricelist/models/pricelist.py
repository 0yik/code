# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pricelist_type = fields.Selection([
        ('sale', 'Sale Pricelist'),('purchase', 'Purchase Pricelist')], String="Applied on")


# class PurchaseConfiguration(models.TransientModel):
#     _inherit = 'purchase.config.settings'
#
#
#     group_purchase_pricelist = fields.Boolean("Use pricelists to adapt your price per customers",
#                                           implied_group='product.group_purchase_pricelist',
#                                           help="""Allows to manage different prices based on rules per category of customers.
#                     Example: 10% for retailers, promotion of 5 EUR on this product, etc.""")
#     group_pricelist_item = fields.Boolean("Show pricelists to customers",
#                                           implied_group='product.group_pricelist_item')
#     group_product_pricelist = fields.Boolean("Show pricelists On Products",
#                                              implied_group='product.group_product_pricelist')