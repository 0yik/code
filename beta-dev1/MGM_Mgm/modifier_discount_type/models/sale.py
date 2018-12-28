from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_discount': order.pricelist_id.currency_id.round(amount_discount),
                'amount_total': amount_untaxed + amount_tax,
            })
            if self.discount_type == 'percent':
                order['amount_discount'] = ((order['amount_untaxed'] * self.discount_rate) / 100) + order['amount_discount']
            else:
                order['amount_discount'] = self.discount_rate + order['amount_discount']

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)
    discount_type = fields.Selection([('percent', 'Percentage'),('amount', 'Fixed Amount')], 'Discount Type',)
    discount_rate = fields.Float(string='Discount Rate', required=1)


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        res = super(SaleOrderLine , self)._compute_amount()
        self.discount_onchange()

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

