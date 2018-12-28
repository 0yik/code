# -*- coding: utf-8 -*-

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _total_discount(self):
        for rec in self:
            discount_amount = 0
            for line in rec.order_line:
                discount_amount += line.discount_amount
            rec.discount_amount = discount_amount
            rec.avg_discount = (discount_amount*100)/rec.amount_untaxed if rec.amount_untaxed else 0

    discount_amount = fields.Float('Total Disocunt', compute="_total_discount", digits=dp.get_precision('Discount'))
    avg_discount = fields.Float('Avg Disocunt', compute="_total_discount", digits=dp.get_precision('Discount'))
    print_discount = fields.Boolean('Print Discount')
    print_discount_amount = fields.Boolean('Print Discount Amount')

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _total_discount(self):
        for rec in self:
            discount = ((rec.disocunt_po*rec.price_unit)/100)
            rec.discount_per_unit = discount
            rec.discount_amount = discount*rec.product_qty
            rec.discounted_unit_price = rec.price_unit - discount

    disocunt_po = fields.Float('Discount (%)')
    discount_amount = fields.Float('Disocunt Amount', compute="_total_discount", digits=dp.get_precision('Discount'))
    discount_per_unit = fields.Float('Discount Per Unit', compute="_total_discount", digits=dp.get_precision('Discount'))
    discounted_unit_price = fields.Float('Discounted Unit Price', compute="_total_discount", digits=dp.get_precision('Discount'))
    multi_discount = fields.Char('Discounts')

    @api.depends('product_qty', 'price_unit', 'taxes_id','multi_discount','disocunt_po')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty,
                                              product=line.product_id, partner=line.order_id.partner_id)
            taxes_total = 0.0
            for tax in line.taxes_id:
                taxes_total += tax.amount
            line.update({
                'price_tax': ((taxes['total_excluded'] - line.discount_amount) * taxes_total) / 100,
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'] - line.discount_amount,
            })

    @api.onchange('multi_discount')
    def _onchange_multi_discount(self):
        def get_disocunt(percentage,amount):
            new_amount = (percentage * amount)/100
            return (amount - new_amount)
        if self.multi_discount:
            amount = 100
            splited_discounts = self.multi_discount.split("+")
            for disocunt_po in splited_discounts:
                amount = get_disocunt(float(disocunt_po),amount)
            self.disocunt_po = 100 - amount
        else:
            self.disocunt_po = 0




