# -*- coding: utf-8 -*-
from odoo import models, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(PurchaseOrderLine, self).onchange_product_id()
        fpos = self.order_id.fiscal_position_id
        self.taxes_id = fpos.map_tax(self.order_id.partner_id.default_tax_ids.filtered(lambda r: r.company_id.id == self.env.user.company_id.id))
        return result

PurchaseOrderLine()