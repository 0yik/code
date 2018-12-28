# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    supplier_id = fields.Char('Supplier SKU')
    foc = fields.Char('FOC', required=False)
    packing = fields.Char('Packing', required=False)
    tax_price = fields.Monetary('Price with tax')