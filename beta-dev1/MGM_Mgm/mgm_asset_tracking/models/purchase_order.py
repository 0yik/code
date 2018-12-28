# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_capital = fields.Boolean('Capital', default=False)
    remaining_asset_qty = fields.Float('Remaining Qty to asset')

    @api.onchange('product_qty')
    @api.multi
    def onchange_po_line_qty(self):
        if self.product_qty:
            self.remaining_asset_qty = self.product_qty