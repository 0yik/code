# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from lxml import etree
import json


class Quant(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = "stock.quant"

    inventory_sale_value = fields.Float('Inventory Sale Value', compute='_compute_inventory_sale_value', readonly=True, store=True)
    sale_price_valuation = fields.Integer( string = 'SPI')

    @api.multi
    def _compute_inventory_sale_value(self):
        for quant in self:
            if quant.company_id != self.env.user.company_id:
                # if the company of the quant is different than the current user company, force the company in the context
                # then re-do a browse to read the property fields for the good company.
                quant = quant.with_context(force_company=quant.company_id.id)
            quant.inventory_sale_value = quant.product_id.list_price * quant.qty
