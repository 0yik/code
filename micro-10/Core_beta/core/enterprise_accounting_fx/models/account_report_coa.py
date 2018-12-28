# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.misc import formatLang
from datetime import datetime, timedelta

class account_context_coa(models.TransientModel):
    _inherit = "account.context.coa"

    def get_columns_names(self):
        columns = [_('Initial Balance (Base)')]
        if self.comparison and (self.periods_number == 1 or self.date_filter_cmp == 'custom'):
            columns += [_('FX Currency'), _('Base Debit'), _('Base Credit')]
        elif self.comparison:
            for period in self.get_cmp_periods(display=True):
                columns += [_('FX Currency'), _('Base Debit'), _('Base Credit')]
        return columns + [_('FX Currency'), _('Base Debit'), _('Base Credit')]

    @api.multi
    def get_columns_types(self):
        types = ['number']
        if self.comparison and (self.periods_number == 1 or self.date_filter_cmp == 'custom'):
            types += ['number', 'number', 'number']
        else:
            for period in self.get_cmp_periods(display=True):
                types += ['number', 'number', 'number']
        return types + ['number', 'number', 'number']

account_context_coa()

class report_account_coa(models.AbstractModel):
    _inherit = "account.coa.report"

    @api.model
    def _lines(self, line_id=None):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_accounts = {}
        period_number = 0
        initial_balances = {}
        context['periods'].reverse()
        for period in context['periods']:
            res = self.with_context(date_from_aml=period[0], date_to=period[1], date_from=period[0] and company_id.compute_fiscalyear_dates(datetime.strptime(period[0], "%Y-%m-%d"))['date_from'] or None).group_by_account_id(line_id)  # Aml go back to the beginning of the user chosen range but the amount on the account line should go back to either the beginning of the fy or the beginning of times depending on the account
            if period_number == 0:
                initial_balances = dict([(k, res[k]['initial_bal']['balance']) for k in res])
            for account in res:
                if account not in grouped_accounts.keys():
                    grouped_accounts[account] = [{'balance': 0, 'debit': 0, 'credit': 0, 'amount_currency': 0} for p in context['periods']]
                grouped_accounts[account][period_number]['debit'] += res[account]['debit']
                grouped_accounts[account][period_number]['credit'] += res[account]['credit']
                grouped_accounts[account][period_number]['amount_currency'] += res[account]['amount_currency']
            period_number += 1
        sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
        initial_bal_total = 0.0
        currency_debit_credit_total = {}
        for p in xrange(len(context['periods'])):
            currency_debit_credit_total.update({p: [0.0, 0.0, 0.0]})
        for account in sorted_accounts:
            currency_debit_credit = []
            initial_bal = [account in initial_balances and self._format(initial_balances[account]) or self._format(0.0)]
            initial_bal_total += (account in initial_balances and initial_balances[account] or 0.0)
            for count in xrange(len(context['periods'])):
                fx_currency = grouped_accounts[account][count].get('amount_currency')
                debit = grouped_accounts[account][count].get('debit')
                credit = grouped_accounts[account][count].get('credit')
                currency_debit_credit.extend([formatLang(self.env, fx_currency), self._format(debit), self._format(credit)])
                currency_debit_credit_total.update(
                    {
                        count: [
                            currency_debit_credit_total.get(count)[0] + fx_currency,
                            currency_debit_credit_total.get(count)[1] + debit,
                            currency_debit_credit_total.get(count)[1] + credit,
                        ]
                    }
                )

            lines.append({
                'id': account.id,
                'type': 'account_id',
                'name': account.code + " " + account.name,
                'footnotes': self.env.context['context_id']._get_footnotes('account_id', account.id),
                'columns': initial_bal + currency_debit_credit,
                'level': 1,
                'unfoldable': False,
            })

        # Total line at bottom
        initial_bal = [self._format(initial_bal_total)]
        debit_credit = []
        for l in currency_debit_credit_total.values():
            for i in l:
                debit_credit.append(self._format(i))

        lines.append({
            'id': 0,
            'type': 'o_account_reports_domain_total',
            'name': _('Total '),
            'footnotes': {},
            'columns': initial_bal + debit_credit,
            'level': 1,
        })
        return lines

report_account_coa()