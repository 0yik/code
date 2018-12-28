# -*- coding: utf-8 -*-

import datetime
from datetime import datetime

from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_month(self):
        for value in self:
            current_month = fields.Date.today().split('-')[1]
            if  value.birth_date:
                birth_month = str(value.birth_date).split('-')[1]
                if birth_month == current_month:
                    value.is_birthdate_month = True

    birth_date = fields.Date(string="Birthdate")
    is_birthdate_month = fields.Boolean(string="BirthDate Discount", compute='_compute_month')


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    membership_birthmonth_discount = fields.Float(string="Birthday Discount(%)")

    @api.depends('price_unit', 'tax_ids', 'qty', 'discount', 'product_id')
    def _compute_amount_line_all(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            taxes = line.tax_ids.filtered(
                lambda tax: tax.company_id.id == line.order_id.company_id.id)
            fiscal_position_id = line.order_id.fiscal_position_id
            if fiscal_position_id:
                taxes = fiscal_position_id.map_tax(taxes, line.product_id, line.order_id.partner_id)
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * (1 - (line.membership_birthmonth_discount or 0.0) / 100.0)
            line.price_subtotal = line.price_subtotal_incl = price * line.qty
            if taxes:
                taxes = taxes.compute_all(
                    price, currency, line.qty, product=line.product_id,
                    partner=line.order_id.partner_id or False)
                line.price_subtotal = taxes['total_excluded']
                line.price_subtotal_incl = taxes['total_included']
            line.price_subtotal = currency.round(line.price_subtotal)
            line.price_subtotal_incl = currency.round(line.price_subtotal_incl)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    birthday_discount = fields.Integer(string="Birthday Month Discount(%)")