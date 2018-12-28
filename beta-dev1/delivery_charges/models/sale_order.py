# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class sales_order(models.Model):
    _inherit = 'sale.order'

    delivery_charge = fields.Float(string="Delivery Charge", compute='get_delivery_charges')

    @api.model
    def get_delivery_charges(self):
        charge_id = self.branch_id.delivery_charge_id
        if charge_id and charge_id.type == 'fixed':
            self.delivery_charge = charge_id.amount
        elif charge_id and charge_id.type == 'percentage':
            self.delivery_charge = self.amount_untaxed*charge_id.amount/100
        else:
            self.delivery_charge = 0

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        super(sales_order, self)._amount_all()
        for order in self:
            delivery_charge = amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                    product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            charge_id = order.branch_id.delivery_charge_id
            if charge_id and charge_id.type == 'fixed':
                delivery_charge = charge_id.amount
            elif charge_id and charge_id.type == 'percentage':
                delivery_charge = amount_untaxed * charge_id.amount / 100

            order.update({
                'delivery_charge': delivery_charge,
                'amount_total': amount_untaxed + amount_tax + delivery_charge,
            })
