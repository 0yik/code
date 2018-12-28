from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_subtotal')
    def _amount_total(self):
        """
        Compute the total amounts of the po.
        """
        for order in self:
            amount_discount = 0

            if order.discount_type and order.discount_rate:
                subtotal = order.amount_untaxed

                if order.discount_type == 'percent':
                    amount_discount = (subtotal * order.discount_rate) / 100
                else:
                    amount_discount = order.discount_rate

            order.update({
                'amount_discount': amount_discount,
                'amount_total': (order.amount_untaxed + order.amount_tax) - amount_discount,
            })



    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits_compute=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_total',
                                   track_visibility='always')
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits_compute=dp.get_precision('Account'), track_visibility='always')


    # @api.onchange('discount_type', 'discount_rate')
    # def discount_onchange(self):
    #     for order in self:
    #         if order.discount_type == 'percent':
    #             for line in order.order_line:
    #                 line.discount = order.discount_rate
    #         else:
    #             total = discount = 0.0
    #             for line in order.order_line:
    #                 total += round((line.product_qty * line.price_unit))
    #             if order.discount_rate != 0:
    #                 discount = (order.discount_rate / total) * 100
    #             else:
    #                 discount = order.discount_rate
    #             for line in order.order_line:
    #                 line.discount = discount


    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        module = self.env['ir.module.module'].search([
            ('name', '=', 'modifier_discount_type')
        ])
        if module and module.state != 'installed':
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in res.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_qty * line.price_unit * line.discount) / 100
            if res.discount_type == 'percent':
                res.amount_discount = (amount_untaxed * res.discount_rate) / 100 + amount_untaxed
                res.amount_total = (amount_untaxed + res.amount_tax)- res.amount_discount
            else:
                res.amount_discount = res.discount_rate + amount_discount
                res.amount_total = (amount_untaxed + res.amount_tax) - res.amount_discount
        return res


    @api.multi
    def write(self, vals):
        module = self.env['ir.module.module'].search([
            ('name', '=', 'modifier_discount_type')
        ])
        if module and module.state != 'installed':
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in self.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_qty * line.price_unit * line.discount) / 100
            if self.discount_type == 'percent':
                vals.update({
                    'amount_discount' : (amount_untaxed * self.discount_rate) / 100 + amount_untaxed,
                    'amount_total' : (amount_untaxed + amount_tax) - amount_discount
                })
            else:
                vals.update({
                    'amount_discount': self.discount_rate + amount_discount,
                   'amount_total' : (amount_untaxed + amount_tax) - amount_discount
                })

        res = super(PurchaseOrder, self).write(vals)

        return res

    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def supply_rate(self):
        for order in self:
            if order.discount_type == 'percent':
                for line in order.order_line:
                    line.discount = order.discount_rate
            else:
                total = discount = 0.0
                for line in order.order_line:
                    total += round((line.product_qty * line.price_unit))
                if order.discount_rate != 0:
                    discount = (order.discount_rate / total) * 100
                else:
                    discount = order.discount_rate
                for line in order.order_line:
                    line.discount = discount


    @api.multi
    def button_dummy(self):
        self.supply_rate()
        return True


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 2), default=0.0)



