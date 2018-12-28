# -*- coding: utf-8 -*-

import json
from odoo.tools import float_is_zero, float_compare
from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class register_aazz(models.Model):
    _inherit = 'account.move.line'

    is_pph = fields.Boolean('Is PPH')

class register_aa(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('move_id.line_ids.amount_residual')
    def _compute_payments(self):
        payment_lines = []
        move_line_search = self.env['account.move.line'].sudo().search([('invoice_id', '=', self.id)])
        for line in self.env['account.move.line'].sudo().search([('invoice_id', '=', self.id)]).filtered(lambda l: l.account_id.id == self.account_id.id):
            payment_lines.extend(filter(None, [rp.credit_move_id.id for rp in line.matched_credit_ids]))
            payment_lines.extend(filter(None, [rp.debit_move_id.id for rp in line.matched_debit_ids]))
        self.payment_move_line_ids = self.env['account.move.line'].browse(list(set(payment_lines)))

    @api.one
    def _get_outstanding_info_JSON(self):
        self.outstanding_credits_debits_widget = json.dumps(False)
        if self.state == 'open':
            domain = [('account_id', '=', self.account_id.id),
                      ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id),
                      ('reconciled', '=', False), ('amount_residual', '!=', 0.0), ('is_pph', '=', True)]
            if self.type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': self.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = self.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == self.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        amount_to_show = line.company_id.currency_id.with_context(date=line.date).compute(
                            abs(line.amount_residual), self.currency_id)
                    if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                        continue
                    info['content'].append({'journal_name': line.ref or line.move_id.name, 'amount': amount_to_show,
                        'currency': currency_id.symbol, 'id': line.id, 'position': currency_id.position,
                        'digits': [69, self.currency_id.decimal_places], })
                info['title'] = type_payment
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True


class register_payment(models.Model):
    _inherit = 'account.payment'

    is_pph = fields.Boolean('Include PPH')
    pph_amount = fields.Float('PPH Amount')
    inv_amount = fields.Float('PPH Amount')

    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        if len(self.invoice_ids) == 0:
            return
        if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
            if self.is_pph and self.pph_amount:
                self.payment_difference = self.amount - self._compute_total_invoices_amount() - self.pph_amount
            else:
                self.payment_difference = self.amount - self._compute_total_invoices_amount()
        else:
            if self.is_pph and self.pph_amount:
                self.payment_difference = self._compute_total_invoices_amount() - self.amount + self.pph_amount
            else:
                self.payment_difference = self._compute_total_invoices_amount() - self.amount

    @api.onchange('is_pph')
    def change_pph(self):
        print "------",self.env.context
        if self.is_pph:
            self.amount = self.inv_amount + self.pph_amount
        else:
            self.amount = self.inv_amount

    @api.model
    def default_get(self, fields):
        rec = super(register_payment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['pph_amount'] = invoice['residual']*0.02
            rec['inv_amount'] = invoice['residual']
        return rec

    @api.model
    def create(self, vals):
        context = self._context
        account_move = self.env['account.move']
        if vals['is_pph'] and context.get('active_model', False) and context.get('active_id', False):
            object = self.env[context['active_model']].browse(context['active_id'])
            # check_amount = object.amount_total + vals['is_pph']
            check_amount = object.amount_total + vals['pph_amount']
            # if vals['amount'] and vals['is_pph'] and vals['amount'] > vals['amount']:
            #     raise ValidationError(_('Sorry, you cannot make payment more than amount asked for.'))
            if float_compare(vals['amount'], check_amount, 2)  > 0 :
                raise ValidationError(_('Sorry, you cannot make payment more than invoice amount + PPH amount   .'))

            object.amount_total += vals['pph_amount']
            # account_obj = self.env['account.account'].search([('name', 'ilike', 'pph')])
            account_obj = self.env['pph.account.config'].search([],limit=1)
            # for account in account_obj:
            #     name = str(account.name)
                # if 'Sales' in name and account.user_type_id.name == 'Current Liabilities':
                #     account_id = account.id
            if object.type in ['out_invoice', 'out_refund']:
                account_id = account_obj.pph_account_sales
            else:
                account_id = account_obj.pph_account_purchase
            object.invoice_line_ids = [
                (0, 0, {'name': 'PPH', 'price_unit': vals['pph_amount'], 'quantity': 1, 'account_id': account_id, })]

            ctx = dict(self._context, lang=object.partner_id.lang)
            journal = object.journal_id.with_context(ctx)
            date = object.date or object.date_invoice
            account_receive_debit = self.env['account.account'].search([('name', 'ilike', 'Trade Receivable Account')], limit=1)
            account_payable_debit = self.env['account.account'].search([('name', 'ilike', 'Trade Payable Account')], limit=1)
            if object.type in ['out_invoice', 'out_refund']:

                line = [(0, 0,{'is_pph': True,
                               'debit': vals['pph_amount'],
                               'name': 'PPH',
                               'price': vals['pph_amount'],
                               # 'account_id': account_debit.id if account_debit else account_id,
                               'account_id':  account_receive_debit.id if account_receive_debit else account_id.id,
                                'date_maturity': object.date_due,
                               'quantity': 1,
                               'invoice_id': object.id,
                               'partner_id': object.partner_id.id
                }),
                (0, 0,{'is_pph': True,
                       'credit': vals['pph_amount'],
                       'name': 'PPH',
                       'price': vals['pph_amount'],
                       'account_id': account_id.id,
                       'date_maturity': object.date_due,
                       'quantity': 1, 'invoice_id': object.id,
                       'partner_id': object.partner_id.id
                })]
            else:
                line = [(0, 0, {'is_pph': True,
                                'debit': vals['pph_amount'],
                                'name': 'PPH',
                                'price': vals['pph_amount'],
                                # 'account_id': account_debit.id if account_debit else account_id,
                                'account_id': account_payable_debit.id if account_payable_debit else account_id.id,
                                'date_maturity': object.date_due,
                                'quantity': 1,
                                'invoice_id': object.id,
                                'partner_id': object.partner_id.id
                                }),
                        (0, 0, {'is_pph': True,
                                'credit': vals['pph_amount'],
                                'name': 'PPH',
                                'price': vals['pph_amount'],
                                'account_id': account_id.id,
                                'date_maturity': object.date_due,
                                'quantity': 1, 'invoice_id': object.id,
                                'partner_id': object.partner_id.id
                                })]

            move_vals = {
                'ref': object.reference,
                 'line_ids': line,
                 'journal_id': journal.id,
                 'date': date,
                 'narration': object.comment,
                 # 'matched_percentage': 1,
            }
            ctx['company_id'] = object.company_id.id
            ctx['invoice'] = object
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            move.matched_percentage = 1
            print "--------move-------",move

            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            # vals = {'move_id': move.id, 'date': date, 'move_name': move.name, 'journal_id': journal.id,}
            # object.with_context(ctx).write(vals)
            # object.action_move_create()




            # company_currency = object.company_id.currency_id
            # diff_currency = object.currency_id != company_currency
            # # create one move line for the total and possibly adjust the other lines amount
            # iml = object.invoice_line_move_line_get()
            # iml += object.tax_line_move_line_get()
            #
            # ctx = dict(self._context, lang=object.partner_id.lang)
            # total, total_currency, iml = object.with_context(ctx).compute_invoice_totals(company_currency, iml)
            # print "----total-",total
            # object.move_id.line_ids = [
            #     (0, 0,
            #     {'type': 'dest', 'name': 'PPH', 'price': total, 'account_id': object.account_id.id,
            #     'date_maturity': object.date_due, 'amount_currency': diff_currency and total_currency,
            #     'currency_id': diff_currency and object.currency_id.id, 'invoice_id': object.id,
            #      'partner_id': object.partner_id.id})]
            #      # 'debit': total,'credit':total})]
            #

        account_payment = super(register_payment, self).create(vals)
        return account_payment


