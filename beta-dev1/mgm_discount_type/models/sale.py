from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.depends('order_line.price_total','discount_type','discount_rate')
    # def _amount_all(self):
    #     for order in self:
    #         amount_untaxed = amount_tax = amount_discount = 0.0
    #         for line in order.order_line:
    #             amount_untaxed += line.price_subtotal
    #             amount_tax += line.price_tax
    #             amount_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
    #         order.update({
    #             'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
    #             'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
    #             'amount_discount': order.pricelist_id.currency_id.round(amount_discount),
    #             'amount_total': amount_untaxed + amount_tax,
    #         })
    #         if self.discount_type == 'percent':
    #             order['amount_discount'] = ((order['amount_untaxed'] * self.discount_rate) / 100) + order['amount_discount']
    #         else:
    #             order['amount_discount'] = self.discount_rate + order['amount_discount']


    @api.depends('order_line.price_subtotal','discount_type', 'discount_rate','additional_amount')
    def _amount_all(self):
        """
        Compute the total amounts of the po.
        """
        unit_price = 0
        total_netto = 0
        discount_rate_value = 0

        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0

            for line in order.order_line:
                unit_price = unit_price + (line.price_unit * line.product_uom_qty)
                total_netto = total_netto + (line.price_unit * line.product_uom_qty) - line.price_subtotal
                amount_untaxed += (line.product_uom_qty * line.price_unit)

                if line.discount_type == 'percent':
                    amount_discount += (line.product_uom_qty * line.price_unit * line.discount_rate) / 100
                    if order.discount_type == 'percent':
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_uom_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
                            discount_rate_value = order.amount_discount

                    else:
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_uom_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = (calculate_discount + order.discount_rate)
                            discount_rate_value = order.amount_discount

                else:
                    amount_discount += (line.discount_rate)
                    if order.discount_type == 'percent':
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_uom_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
                            discount_rate_value = order.amount_discount

                    else:
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_uom_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = (calculate_discount + order.discount_rate)
                            discount_rate_value = order.amount_discount

                amount_tax += line.price_tax

            untaxed_amount = order.currency_id.round(amount_untaxed)


            if order.discount_type and order.discount_rate:
                order.update({
                    'cal_add_price': order.additional_amount,
                    'amount_untaxed': untaxed_amount,
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_discount': order.currency_id.round(discount_rate_value),
                    'amount_total': untaxed_amount - discount_rate_value + amount_tax + order.additional_amount
                })

            else:
                order.update({
                    'cal_add_price': order.additional_amount,
                    'amount_untaxed': untaxed_amount,
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_discount': order.currency_id.round(amount_discount),
                    'amount_total': untaxed_amount - amount_discount + amount_tax + order.additional_amount
                })


    additional_amount = fields.Float('Additional Fee')
    cal_add_price = fields.Monetary(string='Additional Fee', store=True, readonly=True, compute='_amount_all',)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)
    discount_type = fields.Selection([('percent', 'Percentage'),('amount', 'Fixed Amount')], 'Discount Type',)
    discount_rate = fields.Float(string='Discount Rate')


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        self.discount_onchange()
        res = super(SaleOrderLine , self)._compute_amount()
        return res

    @api.onchange('discount_type', 'discount_rate','price_unit')
    def discount_onchange(self):
        for rec in self:
            if rec.discount_type and rec.discount_rate:
                subtotal = rec.price_unit * rec.product_uom_qty
                if rec.discount_type == 'percent':
                    rec.price_subtotal = subtotal - ((subtotal * rec.discount_rate) / 100)
                    rec.discount = rec.discount_rate
                else:
                    rec.price_subtotal = subtotal - rec.discount_rate
                    rec.discount = rec.discount_rate/subtotal * 100

    @api.multi
    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if vals.get('discount_type', False) or vals.get('discount_rate', False):
            subtotal = self.price_unit * self.product_uom_qty
            if self.discount_type == 'percent':
                self.price_subtotal = subtotal - ((subtotal * self.discount_rate) / 100)
            else:
                self.price_subtotal = subtotal - self.discount_rate
        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        subtotal = res.price_unit * res.product_uom_qty

        if res.discount_type == 'percent':
            res.price_subtotal = subtotal - ((subtotal * res.discount_rate) / 100)
        else:
            res.price_subtotal = subtotal - res.discount_rate
        return res

