from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Fixed Amount')], 'Discount Type', )
    discount_rate = fields.Float(string='Discount Rate',)

    @api.depends('product_qty', 'discount_type', 'discount_rate', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        """
        Compute the amounts of the pO line.
        """
        for line in self:
            if line.discount_type == 'percent':
                # price = line.price_unit * (1 - (line.discount_rate or 0.0) / 100.0)
                discount_amount = ((line.price_unit * line.product_qty) * line.discount_rate) / 100
                price = (line.price_unit * line.product_qty) - discount_amount
                taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, 1,
                                                  product=line.product_id, partner=line.order_id.partner_id)
                # taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_qty,
                #                                   product=line.product_id, partner=line.order_id.partner_id)

                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

            else:
                #price = line.price_unit - line.discount_rate
                price = (line.price_unit * line.product_qty) - line.discount_rate
                taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, 1,
                                                  product=line.product_id, partner=line.order_id.partner_id)
                # taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_qty,
                #                                   product=line.product_id, partner=line.order_id.partner_id)
                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })


    @api.onchange('discount_type', 'discount_rate')
    def discount_onchange(self):
        for rec in self:
            if not rec.discount_type:
                rec.discount_rate = 0.0
            if rec.discount_type and rec.discount_rate:
                if rec.discount_type == 'percent':
                    discount_amount = ((rec.price_unit * rec.product_qty) * rec.discount_rate) / 100
                    price = (rec.price_unit * rec.product_qty) - discount_amount
                    taxes = rec.taxes_id.compute_all(price, rec.order_id.currency_id, 1,
                                                     product=rec.product_id, partner=rec.order_id.partner_id)
                    rec.update({
                        'price_tax': taxes['total_included'] - taxes['total_excluded'],
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })

                else:
                    price = (rec.price_unit * rec.product_qty) - rec.discount_rate
                    taxes = rec.taxes_id.compute_all(price, rec.order_id.currency_id, 1,
                                                     product=rec.product_id, partner=rec.order_id.partner_id)
                    rec.update({
                        'price_tax': taxes['total_included'] - taxes['total_excluded'],
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })


# class PurchaseOrder(models.Model):
#     _inherit = "purchase.order"
#
#     @api.depends('order_line.price_subtotal','discount_type','discount_rate')
#     def _calculate_amount_all(self):
#         """
#         Compute the total amounts of the po.
#         """
#         unit_price = 0
#         total_netto = 0
#         discount_rate_value = 0
#
#         for order in self:
#             amount_untaxed = amount_tax = amount_discount = 0.0
#
#             for line in order.order_line:
#                 unit_price = unit_price + (line.price_unit * line.product_qty)
#                 total_netto = total_netto + (line.price_unit * line.product_qty) - line.price_subtotal
#                 amount_untaxed += (line.product_qty * line.price_unit)
#
#                 if line.discount_type == 'percent':
#                     amount_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
#                     if order.discount_type == 'percent':
#                         calculate_discount = 0
#                         if order.discount_rate:
#                             for line in order.order_line:
#                                 calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
#                             order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
#                             discount_rate_value = order.amount_discount
#
#                     else:
#                         calculate_discount = 0
#                         if order.discount_rate:
#                             for line in order.order_line:
#                                 calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
#                             order.amount_discount = (calculate_discount + order.discount_rate)
#                             discount_rate_value = order.amount_discount
#
#                 else:
#                     amount_discount += line.discount_rate
#                     if order.discount_type == 'percent':
#                         calculate_discount = 0
#                         if order.discount_rate:
#                             for line in order.order_line:
#                                 # calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
#                                 calculate_discount += line.discount_rate
#                             order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
#                             discount_rate_value = order.amount_discount
#
#                     else:
#                         calculate_discount = 0
#                         if order.discount_rate:
#                             for line in order.order_line:
#                                 calculate_discount += line.discount_rate
#
#                                 # calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
#                             order.amount_discount = (calculate_discount + order.discount_rate)
#                             discount_rate_value = order.amount_discount
#
#                 amount_tax += line.price_tax
#             untaxed_amount = order.currency_id.round(amount_untaxed)
#
#             if order.discount_type and order.discount_rate:
#                 order.update({
#                     'amount_untaxed': untaxed_amount + discount_rate_value,
#                     'amount_tax': order.currency_id.round(amount_tax),
#                     'amount_discount': order.currency_id.round(discount_rate_value),
#                     'amount_total': untaxed_amount - discount_rate_value + amount_tax,
#                 })
#             else:
#                 order.update({
#                     'amount_untaxed': untaxed_amount + amount_discount,
#                     'amount_tax': order.currency_id.round(amount_tax),
#                     'amount_discount': order.currency_id.round(amount_discount),
#                     'amount_total': untaxed_amount - amount_discount + amount_tax,
#                 })
#
#     amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_calculate_amount_all',
#                                    track_visibility='always')
#     amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_calculate_amount_all',
#                                       digits_compute=dp.get_precision('Account'), track_visibility='always')
#





