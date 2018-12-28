# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _


class IssueVoucherWizard(models.TransientModel):

    _name = 'account.pettycash.fund.voucher'
    _desc = 'Petty Cash Fund Issue Voucher Wizard'

    @api.model
    def _get_fund(self):

        fund_id = self.env.context.get('active_id', False)
        return fund_id

    # Field
    #
    fund = fields.Many2one('account.pettycash.fund', required=True,
                           default=_get_fund)
    date = fields.Date(required=True, default=datetime.today().date())
    partner = fields.Many2one('res.partner')
    lines = fields.One2many('account.pettycash.fund.voucher.line', 'wizard')
    voucher = fields.Many2one('account.voucher')

    @api.multi
    def create_voucher(self):

        Vouchers = self.env['account.voucher']
        for wiz in self:
            lines = []
            total_lines = 0.0
            for line in wiz.lines:
                line_vals = {
                    'name': line.memo,
                    'type': 'dr',
                    'account_id': line.expense_account.id,
                    'amount': line.amount,
                    'price_unit': line.amount,
                    'quantity'  : 1,
                }
                lines.append((0, 0, line_vals))
                total_lines += line.amount
            voucher_vals = {
                'name': _('Petty Cash Expenditure %s' % (wiz.date)),
                'journal_id': wiz.fund.journal.id,
                'account_id': wiz.fund.journal.default_credit_account_id.id,
                'amount': total_lines,
                'petty_cash_fund': wiz.fund.id,
                'partner_id': wiz.partner.id,
                'date': wiz.date,
                'type': 'payment',
                'audit': True,
            }
            # onchange_res = Vouchers.onchange_journal(
            #     wiz.fund.journal.id, [], False, wiz.partner.id, wiz.date,
            #     total_lines, 'payment', False)
            # voucher_vals.update(onchange_res['value'])
            voucher_vals.update({'line_ids': lines})

            wiz.voucher = Vouchers.create(voucher_vals)

        return


class IssueVoucherWizardLine(models.TransientModel):

    _name = 'account.pettycash.fund.voucher.line'
    _desc = 'Petty Cash Fund Issue Voucher Wizard Line'

    # Fields
    #
    wizard = fields.Many2one('account.pettycash.fund.voucher')
    expense_account = fields.Many2one(
        'account.account', required=True,
        domain=[('user_type_id.type', '=', 'other'), ('user_type_id.name', '=', 'Expenses')])
    amount = fields.Float(digits=dp.get_precision('Product Price'),
                          required=True)
    memo = fields.Char()
