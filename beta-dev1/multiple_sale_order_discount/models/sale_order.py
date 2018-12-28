from odoo import api, models, fields
import odoo.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(string='Discount (%)',
                            digits=(16, 2),
                            # digits= dp.get_precision('Discount'),
                            default=0.0)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    @api.depends('order_line.price_subtotal')
    def _compute_amount(self):
        disc = 0.0
        amount_tax=0
        for inv in self:
            for line in inv.order_line:
                disc += (line.product_uom_qty * line.price_unit) * line.discount / 100
                amount_tax += line.price_tax
                print "amont tax"+str(line.price_tax)
        self.amount_untaxed = sum(line.price_subtotal for line in self.order_line)
        self.amount_discount = disc
        self.amount_tax=amount_tax
        print self.amount_tax
        self.amount_total = self.amount_untaxed + self.amount_tax
        self.amount_befor_discount=self.amount_untaxed+self.amount_discount
    amount_befor_discount = fields.Float(string="Amount Before Discount",  required=False,compute='_compute_amount' )

    amount_discount = fields.Float(string='Discount',
                                   digits=dp.get_precision('Account'),
                                   readonly=True, compute='_compute_amount')
    amount_untaxed = fields.Float(string='Subtotal', digits=dp.get_precision('Account'),
                                  readonly=True, compute='_compute_amount', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                readonly=True, compute='_compute_amount')
    discount_ids = fields.One2many(comodel_name="sale.order.discount.line", inverse_name="discount_line_id", string="Discounts", required=False, )

    @api.multi
    def compute_discount(self, discount):
        for order in self:
            val1 = val2 = 0.0
            disc_amnt = 0.0
            for line in order.order_line:
                val1 += (line.product_uom_qty * line.price_unit)
                line.discount = line.discount+discount
                disc_amnt += (line.product_uom_qty * line.price_unit * line.discount)/100
            total = val1 + val2 - disc_amnt
            # self.currency_id = order.pricelist_id.currency_id
            self.amount_discount = disc_amnt
            self.amount_total = total

    @api.onchange('discount_type', 'discount_rate')
    def supply_rate(self):
        for value in self:
            for line_before_discount in value.order_line:
                line_before_discount.discount=0
        for record in self:
            for order in record.discount_ids:
                if order.discount_rate != 0:
                    if order.discount_type == 'percent':
                        self.compute_discount(order.discount_rate)
                    else:
                        total = 0.0
                        for line in record.order_line:
                            total += (line.product_uom_qty * line.price_unit)
                        discount = (order.discount_rate / total) * 100
                        self.compute_discount(discount)
    # @api.model
    # def _prepare_refund(self, invoice, date=None, period_id=None, description=None, journal_id=None):
    #     res = super(AccountInvoice, self)._prepare_refund(invoice, date, period_id,
    #                                                       description, journal_id)
    #     res.update({
    #         'discount_type': self.discount_type,
    #         'discount_rate': self.discount_rate,
    #     })
    #     return res


    @api.multi
    def button_reset_taxes(self):
        self.supply_rate()
        return True



class AccountInvoiceDiscointLine(models.Model):
    _name = 'sale.order.discount.line'
    name = fields.Char()
    discount_type = fields.Selection(string="Discount Type", selection=[('percent', 'Percentage'),
            ('amount', 'Amount') ], required=False, )
    discount_rate = fields.Float(string="Discount Rate",  required=False, )
    discount_line_id = fields.Many2one(comodel_name="sale.order", string="Discount_line", required=False, )
    description = fields.Text(string="Description", required=False, )


