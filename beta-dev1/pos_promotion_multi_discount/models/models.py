# -*- coding: utf-8 -*-

from odoo import models, fields, api


class pos_promotion_multi_discount(models.Model):
    _inherit = 'pos.promotion.discount.order'

    multi_discount = fields.Char(string="Multi Discount")

    @api.onchange('multi_discount')
    def _onchange_multi_discount(self):
        def get_disocunt(percentage, amount):
            new_amount = (percentage * amount)/100
            return (amount - new_amount)
        if self.multi_discount:
            amount = 100
            splited_discounts = self.multi_discount.split("+")
            if ',' in self.multi_discount:
                raise UserError(
                    "You cannot use comma to separate discounts. Please add multiple discounts with '+' notation. \n For example 20 + 5.2")
            for disocunt in splited_discounts:
                amount = get_disocunt(float(disocunt), amount)
            self.discount = 100 - amount
        else:
            self.discount = 0
