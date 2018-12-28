# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _encrypt_product_price(self):
        '''(Method called from a Computed Field 'cost_encrypt_price').
           For encrypt cost price of product. '''

        for record in self:
            record.cost_encrypt_price = self.encript_price(record.product_id.product_tmpl_id and record.product_id.product_tmpl_id.standard_price)

    cost_encrypt_price = fields.Char('Cost Price', compute=_encrypt_product_price)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.cost_encrypt_price = self.encript_price(self.product_id.product_tmpl_id.standard_price)

    def encript_price(self, price):
        encrypts = {
            "0": "Y",
            "1": "A",
            "2": "I",
            "3": "K",
            "4": "C",
            "5": "H",
            "6": "N",
            "7": "M",
            "8": "E",
            "9": "R",
            ".": "O",
        };
        price = "%.2f" % price
        encrypt_price = ''
        for i in price : encrypt_price += encrypts[i]
        return encrypt_price
