# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    rounding_account = fields.Many2one('account.account', 'Rounding Account')



class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    service_charge = fields.Boolean('Apply Service Charge?')
    amount_service = fields.Float(compute='_compute_amount', string='Service Charge', digits=0)
    pos_order_id = fields.Many2one('pos.order', string='From POS')
    rounding = fields.Float(compute='_compute_amount', string='Rounding')

    # @api.one
    # @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    # def _compute_amount(self):
    #     super(AccountInvoice, self)._compute_amount()

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        if not self.pos_order_id:
            super(AccountInvoice, self)._compute_amount()
            return
        self.amount_untaxed = sum(line.price_unit*line.qty for line in self.pos_order_id.lines if not line.is_complimentary)
        self.amount_tax = self.pos_order_id.amount_tax
        
        self.rounding = self.pos_order_id.rounding
        self.amount_service = self.pos_order_id.amount_service
        self.amount_total = self.pos_order_id.amount_total

        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        if not self or not self[0].pos_order_id:
            return super(AccountInvoice, self).action_move_create()
        account_move = self.env['account.move']
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            # iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            iml.append({
                    'type': 'dest',
                    'name': 'Rounding',
                    'price': inv.rounding,
                    'account_id': inv.journal_id.rounding_account.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            if inv.amount_service:
                iml.append({
                        'type': 'src',
                        'name': 'Service Charge',
                        'price': -inv.amount_service,
                        'account_id': inv.branch_id.service_charge_id.service_charge_account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            if inv.amount_tax:
                tax = self.env.ref('pos_price_charges_calculation.pb1_tax_template')
                iml.append({
                        'type': 'src',
                        'name': 'Tax',
                        'price': -inv.amount_tax,
                        'account_id': tax.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(inv.amount_total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = inv.date or inv.date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': inv.amount_total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True

    # @api.multi
    # def get_taxes_values(self):
    #     if not self.service_charge:
    #         return super(AccountInvoice, self).get_taxes_values()
    #     tax = self.env.ref('pos_price_charges_calculation.pb1_tax_template')
    #     tax_grouped = {
    #         'invoice_id': self.id,
    #         'name': tax.name,
    #         'tax_id': tax.id,
    #         'amount': self.pos_order_id.amount_tax,
    #         # 'base': tax.base,
    #         'manual': False,
    #         'sequence': tax.sequence,
    #         'account_analytic_id': tax.analytic or False,
    #         'account_id': self.type in ('out_invoice', 'in_invoice') and (tax.account_id.id) or (tax.refund_account_id),
    #     }
    #     return tax_grouped


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    # service_charge_value = fields.Float(string='Service Charge', digits=0)
    # subtotal_service_charge_value = fields.Float(string='Subtotal Service Charge', digits=0)

    # @api.one
    # @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
    #     'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
    #     'invoice_id.date_invoice', 'service_charge_value')
    # def _compute_price(self):
    #     if not self.invoice_id.service_charge:
    #         return super(AccountInvoiceLine, self)._compute_price()
    #     currency = self.invoice_id and self.invoice_id.currency_id or None
    #     price = (self.price_unit * (1 - (self.discount or 0.0) / 100.0)) + self.service_charge_value
    #     print "PRICE   ",price
    #     taxes = False
    #     if self.invoice_line_tax_ids:
    #         taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
    #     self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
    #     if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
    #         price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
    #     sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
    #     self.price_subtotal_signed = price_subtotal_signed * sign

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
