# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    @api.model
    def _get_invoice(self):
        invoice_ids = []
        invoice_search = self.env['account.invoice'].search([('type', '=', 'in_invoice'),('origin', 'ilike', 'PO'),('state', 'in', ('open','paid'))])
        for inv in  invoice_search:
            purchase_br = self.env['purchase.order'].search([('name', '=', inv.origin)])
            for line in purchase_br.order_line:
                if line.is_capital and line.remaining_asset_qty:
                    invoice_ids.append(inv.id)
                    break
        return [('id', 'in', invoice_ids and invoice_ids or [])]

    invoice_id = fields.Many2one('account.invoice', string="Invoice", domain=_get_invoice)
    is_asset_proceeded = fields.Boolean('Asset Proceeded', default=False)