from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.depends('lines', 'lines.discount', 'lines.price_unit')
    def compute_amount(self):
        food_categ_id = self.env['ir.model.data'].xmlid_to_res_id('report_tax_auditor.pos_categ_food')
        drink_categ_id = self.env['ir.model.data'].xmlid_to_res_id('report_tax_auditor.pos_categ_drink')
        for record in self:
            food_amount, drink_amount = 0.0, 0.0
            food_drink_tax = 0.0
            service_charge = 0.0
            discount_amount = 0.0
            for line in record.lines:
                if line.product_id.pos_categ_id.id == food_categ_id:
                    food_amount += ((line.price_unit * line.qty) - line.amount_discount)
                    food_drink_tax += line.amount_tax
                elif line.product_id.pos_categ_id.id == drink_categ_id:
                    drink_amount += ((line.price_unit * line.qty) - line.amount_discount)
                    food_drink_tax += line.amount_tax
                service_charge += line.subtotal_service_charge_value
                discount_amount += line.amount_discount
            record.total_food_amount = food_amount
            record.total_drink_amount = drink_amount
            record.total_food_drink_tax = food_drink_tax
            record.total_service_charge = service_charge
            record.total_discount_amount = discount_amount
            value = food_amount + drink_amount
            if value > 100 and (value%100 != 0):
                diff = value%100
                if diff < 50:
                    value -= diff
                else:
                    value += (100-diff)
            record.total_rounding_amount = value

    @api.depends('statement_ids')
    def compute_amount_given(self):
        for record in self:
            amount = 0.0
            for line in record.statement_ids:
                if line.amount > 0:
                    amount += line.amount
            record.amount_given_by_customer = amount

    @api.depends('pos_reference')
    def compute_pos_reference(self):
        for record in self:
            if record.pos_reference:
                data = record.pos_reference.split(' ')
                record.pos_reference_no = data and data[1]

    total_food_amount = fields.Float(compute='compute_amount', string='Food Amount')
    total_drink_amount = fields.Float(compute='compute_amount', string='Drink Amount')
    total_food_drink_tax = fields.Float(compute='compute_amount', string='Tax Amount')
    total_service_charge = fields.Float(compute='compute_amount', string='Total Service Charge')
    total_rounding_amount = fields.Float(compute='compute_amount', string='Rounding Amount')
    total_discount_amount = fields.Float(compute='compute_amount', string='Discount Amount')
    amount_given_by_customer = fields.Float(compute='compute_amount_given', string='Amount Given')
    pos_reference_no = fields.Char(compute='compute_pos_reference', string='POS Reference')

PosOrder()

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.depends('tax_ids','price_unit')
    def compute_tax(self):
        for record in self:
            taxes = record.tax_ids.filtered(lambda t: t.company_id.id == record.order_id.company_id.id)
            if record.order_id.fiscal_position_id:
                taxes = record.order_id.fiscal_position_id.map_tax(taxes, record.product_id, record.order_id.partner_id)
            price = record.price_unit * (1 - (record.discount or 0.0) / 100.0)
            taxes = taxes.compute_all(price, record.order_id.pricelist_id.currency_id, record.qty, product=record.product_id, partner=record.order_id.partner_id or False)['taxes']
            record.amount_tax = sum(tax.get('amount', 0.0) for tax in taxes)

    @api.depends('discount', 'price_unit')
    def compute_discount(self):
        for record in self:
            record.amount_discount = record.discount and ((record.discount / 100) * (record.price_unit * record.qty)) or 0.0

    amount_tax = fields.Float(compute='compute_tax', string='Tax')
    amount_discount = fields.Float(compute='compute_discount', string='Discount Amount')

PosOrderLine()