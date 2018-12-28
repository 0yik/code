# -*- coding: utf-8 -*-


import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WarningOnSaleInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        total_inv = 0
        for invoices in self.env['account.invoice'].search([('origin','=',order.name),('state','!=','cancel')]):
            total_inv += invoices.amount_untaxed
        total_inv += amount
        if total_inv > order.amount_total:
            raise UserError(_('You are trying to create invoice more than total price...!!'))
        res = super(WarningOnSaleInvoice, self)._create_invoice(order, so_line, amount)
        return res

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        remaining_amount = total_inv = 0
        if self.advance_payment_method == 'percentage' or "fixed":
            order = self.env['sale.order'].browse(self._context.get('active_ids'))[0]
            for invoices in self.env['account.invoice'].search([('origin', '=', order.name), ('state', '!=', 'cancel')]):
                total_inv += invoices.amount_untaxed

            if total_inv < order.amount_untaxed:
                if self.advance_payment_method == 'percentage':
                    remaining_amount = 100 - ((100 * total_inv) / (order.amount_untaxed - order.amount_discount))
                else:
                    remaining_amount = order.amount_untaxed - total_inv
            return {'value': {'amount': remaining_amount}}
        return {}

    @api.multi
    def create_invoices(self):
        if self.rate > 0.0 and self.currency_id.id == self.currency_to_id.id:
            raise UserError(_("Currency From and Currency To both are same, so Exchange rate should be 0.0"))

        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            if self.rate:
                rate_new = self.rate
                currency_to_id = self.currency_to_id.id
                sale_orders.with_context(rate=self.rate, currency_id=self.currency_to_id.id).action_invoice_create()
            else:
                sale_orders.action_invoice_create()

        elif self.advance_payment_method == 'all':
            if self.rate:
                rate_new = self.rate
                currency_to_id = self.currency_to_id.id
                sale_orders.with_context(rate=self.rate, currency_id=self.currency_to_id.id).action_invoice_create(
                    final=True)
            else:
                rate_new = 0.0
                currency_to_id = False
                grouped = False
                sale_orders.action_invoice_create(final=True)

        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.values'].sudo().set_default('sale.config.settings', 'deposit_product_id_setting',
                                                         self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            amount_percentage = 0
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':

                    amount_percentage = self.amount

                    if self.rate:
                        amount = ((order.amount_untaxed - order.amount_discount) * self.rate) * (self.amount * self.rate) / 100
                        amount_invoice = ((order.amount_total) * self.rate) * (self.amount * self.rate) / 100
                    else:
                        amount = (order.amount_untaxed - order.amount_discount) * self.amount / 100
                        amount_invoice = (order.amount_total) * self.amount / 100
                else:

                    amount_percentage = (self.amount / order.amount_untaxed) * 100

                    if self.rate:
                        amount = self.amount * self.rate
                        amount_invoice = self.amount * self.rate
                    else:
                        amount = self.amount
                        amount_invoice = self.amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_(
                        'The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_(
                        "The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(
                    lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids
                context = {'lang': order.partner_id.lang}
                so_line = sale_line_obj.create({
                    # 'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'name': _('Advance: %s, %s ') % (time.strftime('%m %Y'), str(amount_percentage)+"%", ),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'tax_id': [(6, 0, tax_ids)],
                })

                del context
                self._create_invoice(order, so_line, amount_invoice)

        if self.rate:
            # 'name': datetime.today()
            self.env['res.currency.rate'].create({'name': self.date,
                                                  'rate': self.rate,
                                                  'currency_id': self.currency_to_id.id})
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}





