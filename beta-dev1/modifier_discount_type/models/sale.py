from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)
    discount_type = fields.Selection([('percent', 'Percentage'),('amount', 'Fixed Amount')], 'Discount Type',)
    discount_rate = fields.Float(string='Discount Rate', required=0)

    @api.onchange('discount_type', 'discount_rate')
    def discount_onchange(self):
        for rec in self:
            if rec.discount_type and rec.discount_rate:
                subtotal = rec.price_unit * rec.product_uom_qty
                if rec.discount_type == 'percent':
                    rec.price_subtotal = subtotal - ((subtotal * rec.discount_rate) / 100)
                else:
                    rec.price_subtotal = subtotal - rec.discount_rate

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

