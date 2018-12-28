# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.misc import formatLang
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class account_context_general_ledger(models.TransientModel):
    _inherit = "account.context.general.ledger"

    def get_columns_names(self):
        return [_("Date"), _("Reference"), _("Label"), _("Partner"), _("FX Currency Rate"), _("FX Currency"), _("Base Debit"), _("Base Credit"), _("Balance (Base)")]

    @api.multi
    def get_columns_types(self):
        return ["date", "text", "text", "text", "number", "number", "number","number", "number"]

account_context_general_ledger()

class report_account_general_ledger(models.AbstractModel):
    _inherit = "account.general.ledger"

    @api.model
    def _lines(self, line_id=None):
        lang_code = self.env.lang or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        lines = []
        total_debit = 0.0
        total_credit = 0.0
        total_balance = 0.0
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_accounts = self.with_context(date_from_aml=context['date_from'], date_from=context['date_from'] and company_id.compute_fiscalyear_dates(datetime.strptime(context['date_from'], "%Y-%m-%d"))['date_from'] or None).group_by_account_id(line_id)  # Aml go back to the beginning of the user chosen range but the amount on the account line should go back to either the beginning of the fy or the beginning of times depending on the account
        sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
        unfold_all = context.get('print_mode') and not context['context_id']['unfolded_accounts']
        for account in sorted_accounts:
            debit = grouped_accounts[account]['debit']
            credit = grouped_accounts[account]['credit']
            balance = grouped_accounts[account]['balance']
            total_debit += debit
            total_credit += credit
            total_balance += balance
            amount_currency = '' if not account.currency_id else self._format(grouped_accounts[account]['amount_currency'], currency=account.currency_id)
            amount_currency_rate = account.currency_id.rate if account.currency_id.rate else ''
            lines.append({
                'id': account.id,
                'type': 'line',
                'name': account.code + " " + account.name,
                'footnotes': self.env.context['context_id']._get_footnotes('line', account.id),
                'columns': ['', amount_currency_rate, amount_currency, self._format(debit), self._format(credit), self._format(balance)],
                'level': 2,
                'unfoldable': True,
                'unfolded': account in context['context_id']['unfolded_accounts'] or unfold_all,
                'colspan': 4,
            })
            if account in context['context_id']['unfolded_accounts'] or unfold_all:
                initial_debit = grouped_accounts[account]['initial_bal']['debit']
                initial_credit = grouped_accounts[account]['initial_bal']['credit']
                initial_balance = grouped_accounts[account]['initial_bal']['balance']
                total_debit += initial_debit
                total_credit += initial_credit
                total_balance += initial_balance
                initial_currency = '' if not account.currency_id else self._format(grouped_accounts[account]['initial_bal']['amount_currency'], currency=account.currency_id)
                initial_currency_rate = account.currency_id.rate if account.currency_id.rate else ''
                domain_lines = [{
                    'id': account.id,
                    'type': 'initial_balance',
                    'name': _('Initial Balance'),
                    'footnotes': self.env.context['context_id']._get_footnotes('initial_balance', account.id),
                    'columns': ['', '', '', '', initial_currency_rate, initial_currency, self._format(initial_debit), self._format(initial_credit), self._format(initial_balance)],
                    'level': 1,
                }]
                progress = initial_balance
                amls = grouped_accounts[account]['lines']
                used_currency = self.env.user.company_id.currency_id
                for line in amls:
                    if self.env.context['cash_basis']:
                        line_debit = line.debit_cash_basis
                        line_credit = line.credit_cash_basis
                    else:
                        line_debit = line.debit
                        line_credit = line.credit
                    line_debit = line.company_id.currency_id.compute(line_debit, used_currency)
                    line_credit = line.company_id.currency_id.compute(line_credit, used_currency)
                    progress = progress + line_debit - line_credit
                    currency = "" if not line.currency_id else self.with_context(no_format=False)._format(line.amount_currency, currency=line.currency_id)
                    currency_rate =  line.currency_id.rate   if line.currency_id.rate else ''
                    name = []
                    name = line.name and line.name or ''
                    if line.ref:
                        name = name and name + ' - ' + line.ref or line.ref
                    if len(name) > 35 and not self.env.context.get('no_format'):
                        name = name[:32] + "..."
                    partner_name = line.partner_id.name
                    if partner_name and len(partner_name) > 35 and not self.env.context.get('no_format'):
                        partner_name = partner_name[:32] + "..."
                    domain_lines.append({
                        'id': line.id,
                        'type': 'move_line_id',
                        'move_id': line.move_id.id,
                        'action': line.get_model_id_and_name(),
                        'name': line.move_id.name if line.move_id.name else '/',
                        'footnotes': self.env.context['context_id']._get_footnotes('move_line_id', line.id),
                        'columns': [
                            datetime.strptime(line.date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),
                            line.ref, line.name, partner_name, currency_rate, currency, line_debit != 0 and self._format(line_debit) or '',
                            line_credit != 0 and self._format(line_credit) or '', self._format(progress)
                        ],
                        'level': 1,
                    })
                domain_lines.append({
                    'id': account.id,
                    'type': 'o_account_reports_domain_total',
                    'name': _('Total '),
                    'footnotes': self.env.context['context_id']._get_footnotes('o_account_reports_domain_total', account.id),
                    'columns': ['', '', '', '', amount_currency_rate, amount_currency, self._format(debit), self._format(credit), self._format(balance)],
                    'level': 1,
                })
                lines += domain_lines

        if len(context['context_id'].journal_ids) == 1 and context['context_id'].journal_ids.type in ['sale', 'purchase'] and not line_id:
            total = self._get_journal_total()
            lines.append({
                'id': 0,
                'type': 'total',
                'name': _('Total'),
                'footnotes': {},
                'columns': ['', '', '', '', '',self._format(total['debit']), self._format(total['credit']), self._format(total['balance'])],
                'level': 1,
                'unfoldable': False,
                'unfolded': False,
            })
            lines.append({
                'id': 0,
                'type': 'line',
                'name': _('Tax Declaration'),
                'footnotes': {},
                'columns': ['', '', '', '', '', '', ''],
                'level': 1,
                'unfoldable': False,
                'unfolded': False,
            })
            lines.append({
                'id': 0,
                'type': 'line',
                'name': _('Name'),
                'footnotes': {},
                'columns': ['', '', '', '', _('Base Amount'), _('Tax Amount'), ''],
                'level': 2,
                'unfoldable': False,
                'unfolded': False,
            })
            for tax, values in self._get_taxes().items():
                lines.append({
                    'id': tax.id,
                    'name': tax.name + ' (' + str(tax.amount) + ')',
                    'type': 'tax_id',
                    'footnotes': self.env.context['context_id']._get_footnotes('tax_id', tax.id),
                    'unfoldable': False,
                    'columns': ['', '', '', '', values['base_amount'], values['tax_amount'], ''],
                    'level': 1,
                })
        # Total line at bottom
        if not line_id:
            lines.append({
                'id': 0,
                'type': 'o_account_reports_domain_total',
                'name': _('Total '),
                'footnotes': {},
                'columns': ['', '', '', '', '', '', self._format(total_debit), self._format(total_credit), self._format(total_balance)],
                'level': 1,
            })
        return lines

report_account_general_ledger()