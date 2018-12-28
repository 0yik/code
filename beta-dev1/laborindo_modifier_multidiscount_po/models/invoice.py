# -*- coding: utf-8 -*-

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _total_discount_po(self):
        for rec in self:
            discount_amount_po = 0
            for line in rec.invoice_line_ids:
                discount_amount_po += line.discount_amount_po
            rec.discount_amount_po = discount_amount_po
            rec.avg_discount_po = (discount_amount_po*100)/rec.amount_untaxed if rec.amount_untaxed else 0


    discount_amount_po = fields.Float('Total Disocunt', compute="_total_discount_po", digits=dp.get_precision('Discount'))
    avg_discount_po = fields.Float('Avg Disocunt', compute="_total_discount_po", digits=dp.get_precision('Discount'))
    print_discount_po = fields.Boolean('Print Discount')
    print_discount_amount_po = fields.Boolean('Print Discount Amount')

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        res.update({'multi_discount_po': line.multi_discount,
                    'discounted_unit_price_po': line.discounted_unit_price,
                    'discount_per_unit_po': line.discount_per_unit,
                    'discount': line.disocunt_po,
                    'discount_amount_po': line.discount_amount})
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _total_discount_po(self):
        for rec in self:
            discount = ((rec.discount*rec.price_unit)/100)
            rec.discount_per_unit_po = discount
            rec.discount_amount_po = discount*rec.quantity
            rec.discounted_unit_price_po = rec.price_unit - discount

    discount_amount_po = fields.Float('Discount Amount', compute="_total_discount_po", digits=dp.get_precision('Discount'))
    discount_per_unit_po = fields.Float('Discount Per Unit', compute="_total_discount_po", digits=dp.get_precision('Discount'))
    multi_discount_po = fields.Char('Discounts')
    discounted_unit_price_po = fields.Float('Discounted Unit Price', compute="_total_discount_po", digits=dp.get_precision('Discount'))


    @api.onchange('multi_discount_po')
    def _onchange_multi_discount(self):
        def get_disocunt(percentage,amount):
            new_amount = (percentage * amount)/100
            return (amount - new_amount)
        if self.multi_discount_po:
            amount = 100
            splited_discounts = self.multi_discount_po.split("+")
            for disocunt in splited_discounts:
                amount = get_disocunt(float(disocunt),amount)
            self.discount = 100 - amount
        else:
            self.discount = 0

