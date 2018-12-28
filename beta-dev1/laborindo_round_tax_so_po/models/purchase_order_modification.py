# coding=utf-8
from odoo import api, fields, models, _
# import math

# class PurchaseOrderModification(models.Model):
#     _inherit = 'purchase.order'
#
#     @api.onchange('order_line')
#     def onchange_order_line_rounding(self):
#         for rec in self:
#             print ">>>>>>>>Gracias"
#             # rec.order_line.price_subtotal = round(rec.order_line.price_subtotal)
#             rec.amount_tax = round(rec.amount_tax)
#             for line in rec.order_line:
#                 print ">>>>>>>>>>>>>>>",line.price_subtotal, round(line.price_subtotal)
#                 line.price_subtotal = round(line.price_subtotal)
#                 print "22222222222222",line.price_subtotal
#

class PurchaseOrderLineModifications(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        res = super(PurchaseOrderLineModifications, self)._compute_amount()
        for line in self:
            line.price_subtotal = round(line.price_subtotal)
            line.price_tax = round(line.price_tax)
        # 2/0
        return res


class AccountInvoiceLineModifications(models.Model):
    _inherit = 'account.invoice.line'

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        res = super(AccountInvoiceLineModifications, self)._compute_amount()
        for line in self:
            line.price_subtotal = round(line.price_subtotal)
            line.price_tax = round(line.price_tax)
        # 2/0
        return res
