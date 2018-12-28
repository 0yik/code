from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
import json

class sale_to_invoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    ppn_type    = fields.Selection([('include','Include PPN'),('exclude','Exclude PPN')],string="PPN Type")
    ppn_amount  = fields.Float('PPN Amount')

    @api.onchange('ppn_type','advance_payment_method','amount')
    def ppn_amount_onchange(self):
        if self.advance_payment_method:
            if self.advance_payment_method == 'percentage':
                if self.ppn_type:
                    if self.ppn_type == 'exclude':
                        if self.env.context.get('active_ids',False) and self.env.context.get('active_model',False) == 'sale.order':
                            self.ppn_amount = self.env['sale.order'].browse(self.env.context.get('active_ids',False)).amount_untaxed  * (self.amount /100) * 0.1
                    else:
                        self.ppn_amount = 0
            else:
                if self.ppn_type:
                    if self.ppn_type == 'exclude':
                        self.ppn_amount = self.amount * 0.1
                    else:
                        self.ppn_amount = 0

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _(
                    'There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        ppn_amount = 0
        if self.advance_payment_method == 'percentage':
            if self.ppn_type == 'include':
                amount = order.amount_untaxed * (self.amount /1.1) / 100
                name = _("Down payment of %s") % (order.name,)
            else:
                amount = order.amount_untaxed * self.amount / 100
                ppn_amount = self.ppn_amount
                name = _("Down payment of %s") % (order.name,)
        elif self.advance_payment_method == 'fixed':
            if self.ppn_type == 'include':
                amount = self.amount / 1.1
                name = _('Down Payment')
            else:
                amount = self.amount
                ppn_amount = self.ppn_amount
                name = _('Down Payment')
        else:
            amount = self.amount
            name = _('Down Payment')
        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids
        if self.ppn_type == 'include' and self.advance_payment_method in ('fixed','percentage'):
            tax = self.env['account.tax'].search([('name','=','Down Payment')],limit=1)
            if tax:
                tax_ids.append(tax.id)
        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'advance_payment_method': self.advance_payment_method,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                'account_analytic_id': order.project_id.id or False,
            })],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'user_id': order.user_id.id,
            'comment': order.note,
            'ppn_amount': ppn_amount or 0,
        })
        if self.advance_payment_method in ('fixed','percentage'):
            invoice.write({'ppn_type':self.ppn_type})
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                                       values={'self': invoice, 'origin': order},
                                       subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.project_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            # 'sale_order_id': self.order_id.id or False
        }
        if qty < 0:
            if 'include' in self.order_id.invoice_ids.mapped('ppn_type'):
                res.update({'price_unit':self.price_unit/1.1})
                tax_id = self.env['account.tax'].search([('name','=','Down Payment')],limit=1)
                if tax_id:
                    tax_ids = self.tax_id.ids
                    tax_ids.append(tax_id.id)
                    res.update({'invoice_line_tax_ids': [(6, 0, tax_ids)]})
            elif 'exclude' in self.order_id.invoice_ids.mapped('ppn_type'):
                invoice = self.order_id.invoice_ids.filtered(lambda record:record.ppn_type == 'exclude')
                invoice_id = self.env['account.invoice'].search([('id','in',self.order_id.invoice_ids.ids)],order='id desc',limit=1)
                invoice_id.write({'ppn_amount':invoice[0].ppn_amount * -1})
        return res

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    ppn_amount  = fields.Float()
    ppn_type    = fields.Selection([('include', 'Include PPN'), ('exclude', 'Exclude PPN')], string="PPN Type")
    advance_payment_method = fields.Char('Advance payment method')
    # sale_order_id   = fields.Many2one('sale.order')

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice','type')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids) + self.ppn_amount
        self.amount_total = self.amount_untaxed + self.amount_tax
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

    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        if self.sudo().move_id.line_ids.ids:
            residual = 0.0
            # residual_company_signed = 0.0 + self.ppn_amount
        for line in self.sudo().move_id.line_ids:
            if line.account_id.internal_type in ('receivable', 'payable') and not line.name == 'Stamp':
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                    residual += from_currency.compute(line.amount_residual, self.currency_id)
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

    # @api.model
    # def create(self,vals):
    #     res = super(account_invoice, self).create(vals)
    #     if res.advance_payment_method not in ['fixed','percentage']:
    #         res.write({'sale_order_id': self.env['sale.order'].search([]).filtered(lambda record: res.id in record.invoice_ids.ids).id or False})
    #     return res

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
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
            sale_order_id = self.env['sale.order'].search([]).filtered(lambda record:self.id in record.invoice_ids.ids)
            if not (sale_order_id and sale_order_id.tax_term == 'customer'):
                iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = \
                inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total,inv.date_invoice)[0]
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
                    'price': total,
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

    @api.one
    @api.depends('payment_move_line_ids.amount_residual')
    def _get_payment_info_JSON(self):
        self.payments_widget = json.dumps(False)
        if self.payment_move_line_ids:
            info = {'title': _('Less Payment'), 'outstanding': False, 'content': []}
            currency_id = self.currency_id
            for payment in self.payment_move_line_ids.filtered(lambda record:record.name != 'Stamp'):
                payment_currency_id = False
                if self.type in ('out_invoice', 'in_refund'):
                    amount = sum(
                        [p.amount for p in payment.matched_debit_ids if p.debit_move_id in self.move_id.line_ids])
                    amount_currency = sum([p.amount_currency for p in payment.matched_debit_ids if
                                           p.debit_move_id in self.move_id.line_ids])
                    if payment.matched_debit_ids:
                        payment_currency_id = all([p.currency_id == payment.matched_debit_ids[0].currency_id for p in
                                                   payment.matched_debit_ids]) and payment.matched_debit_ids[
                                                  0].currency_id or False
                elif self.type in ('in_invoice', 'out_refund'):
                    amount = sum(
                        [p.amount for p in payment.matched_credit_ids if p.credit_move_id in self.move_id.line_ids])
                    amount_currency = sum([p.amount_currency for p in payment.matched_credit_ids if
                                           p.credit_move_id in self.move_id.line_ids])
                    if payment.matched_credit_ids:
                        payment_currency_id = all([p.currency_id == payment.matched_credit_ids[0].currency_id for p in
                                                   payment.matched_credit_ids]) and payment.matched_credit_ids[
                                                  0].currency_id or False
                # get the payment value in invoice currency
                if payment_currency_id and payment_currency_id == self.currency_id:
                    amount_to_show = amount_currency
                else:
                    amount_to_show = payment.company_id.currency_id.with_context(date=payment.date).compute(amount,self.currency_id)
                if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                    continue
                payment_ref = payment.move_id.name
                if payment.move_id.ref:
                    payment_ref += ' (' + payment.move_id.ref + ')'
                info['content'].append({
                    'name': payment.name,
                    'journal_name': payment.journal_id.name,
                    'amount': amount_to_show,
                    'currency': currency_id.symbol,
                    'digits': [69, currency_id.decimal_places],
                    'position': currency_id.position,
                    'date': payment.date,
                    'payment_id': payment.id,
                    'move_id': payment.move_id.id,
                    'ref': payment_ref,
                })
            if self.payment_move_line_ids.filtered(lambda record:record.name == 'Stamp'):
                info['content'][-1].update({'amount': self.payment_ids[-1].amount})
            self.payments_widget = json.dumps(info)

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.multi
    def _compute_sales_to_invoice_amount(self):
        amounts = self.env['sale.order'].read_group([
            ('team_id', 'in', self.ids),
            ('invoice_status', '=', 'to invoice'),
        ], ['amount_total', 'team_id'], ['team_id'])
        for rec in amounts:
            self.browse(rec['team_id'][0]).sales_to_invoice_amount = rec.get('amount_total')

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.model
    def add_stamp_product(self,invoice):
        stamp = 0
        if self.amount_total >= 250000 and self.amount_total <= 1000000:
            stamp = 3000
        elif self.amount_total > 1000000:
            stamp = 6000
        if stamp != 0:
            product_id = self.env['product.product'].search([('name', '=', 'Stamp')])
            if not product_id:
                product_id = self.env['product.product'].create({
                    'name': 'Stamp',
                    'type': 'service'
                })
            invoice.write({'invoice_line_ids': [(0, 0, {
                'product_id': product_id.id,
                'order_id': self.id,
                'price_unit': stamp,
                'account_id': invoice.account_id.id,
                'quantity'  : 1,
                'name'      : 'Stamp'
            })]})


    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    order.add_stamp_product(invoice)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(
                            ', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)
                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                                           values={'self': invoice, 'origin': references[invoice]},
                                           subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self,vals):
        if self._context.get('invoice',False):
            if vals.get('credit',False):
                vals.update({'credit':vals.get('credit',False)+ self._context.get('invoice',False).ppn_amount})
            elif vals.get('debit',False):
                vals.update({'debit': vals.get('debit', False) + self._context.get('invoice', False).ppn_amount})
        res = super(account_move_line, self).create(vals)
        return res