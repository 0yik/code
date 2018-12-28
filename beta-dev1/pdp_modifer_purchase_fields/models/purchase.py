from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_rate','additional_amount')
    def _calculate_amount_all(self):

        """
        Compute the total amounts of the po.
        """
        discount_rate_value = 0

        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0

            for line in order.order_line:
                # unit_price = unit_price + (line.price_unit * line.product_qty)
                # total_netto = total_netto + (line.price_unit * line.product_qty) - line.price_subtotal
                amount_untaxed += (line.product_qty * line.price_unit)

                if line.discount_type == 'percent':
                    amount_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                    if order.discount_type == 'percent':
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
                            discount_rate_value = order.amount_discount

                    else:
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = (calculate_discount + order.discount_rate)
                            discount_rate_value = order.amount_discount

                else:
                    amount_discount += line.discount_rate
                    if order.discount_type == 'percent':
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += line.discount_rate
                                # calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
                            discount_rate_value = order.amount_discount

                    else:
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += line.discount_rate
                                #calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = (calculate_discount + order.discount_rate)
                            discount_rate_value = order.amount_discount

                amount_tax += line.price_tax

            untaxed_amount = order.currency_id.round(amount_untaxed)

            if order.discount_type and order.discount_rate:
                order.update({
                    'cal_add_price': order.additional_amount,
                    'amount_untaxed': untaxed_amount ,
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_discount': order.currency_id.round(discount_rate_value),
                    'amount_total': untaxed_amount - discount_rate_value + amount_tax + order.additional_amount,
                })
            else:
                order.update({
                    'cal_add_price': order.additional_amount,
                    'amount_untaxed': untaxed_amount,
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_discount': order.currency_id.round(amount_discount),
                    'amount_total': untaxed_amount - amount_discount + amount_tax + order.additional_amount,
                })

    additional_amount = fields.Float('Additional Fee')
    cal_add_price = fields.Monetary(string='Additional Fee', store=True, readonly=True, compute='_calculate_amount_all',)

