# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random

class AccountFinancialReportContext(models.TransientModel):
    _inherit = "account.financial.html.report.context"

    def get_columns_names(self):
        columns = []
        if self.report_id.debit_credit and not self.comparison:
            columns += [_('Debit'), _('Credit')]
        # Adding forecast column
        if self.report_id.name in ('Balance Sheet','Profit and Loss','Cash Flow Statement','Executive Summary'):
            columns += ['Forecast']
        columns += [self.get_balance_date()]
        if self.comparison:
            if self.report_id.name in ('Balance Sheet','Profit and Loss','Cash Flow Statement','Executive Summary'):
                if self.periods_number == 1 or self.date_filter_cmp == 'custom':
                    columns += ['Forecast', self.get_cmp_date(), '%']
                else:
                    period_columns = []
                    count = 0
                    for item in self.get_cmp_periods(display=True):
                        if not (count % 2):
                            period_columns.append('Forecast')
                        period_columns.append(item)
                    columns += period_columns
            else:
                if self.periods_number == 1 or self.date_filter_cmp == 'custom':
                    columns += [self.get_cmp_date(), '%']
                else:
                    columns += self.get_cmp_periods(display=True)
        return columns

    @api.multi
    def get_columns_types(self):
        types = []
        if self.report_id.debit_credit and not self.comparison:
            types += ['number', 'number']
        # Adding forecast type
        if self.report_id.name in ('Balance Sheet','Profit and Loss','Cash Flow Statement','Executive Summary'):
            types += ['number']
        types += ['number']
        if self.comparison:
            if self.report_id.name in ('Balance Sheet', 'Profit and Loss', 'Cash Flow Statement', 'Executive Summary'):
                if self.periods_number == 1 or self.date_filter_cmp == 'custom':
                    types += ['number', 'number', 'number']
                else:
                    types += (['number', 'number'] * self.periods_number)
            else:
                if self.periods_number == 1 or self.date_filter_cmp == 'custom':
                    types += ['number', 'number']
                else:
                    types += (['number'] * self.periods_number)
        return types

AccountFinancialReportContext()

class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    @api.multi
    def get_lines(self, financial_report, context, currency_table, linesDicts):
        final_result_table = []
        comparison_table = context.get_periods()
        currency_precision = self.env.user.company_id.currency_id.rounding
        # build comparison table

        for line in self:
            res = []
            debit_credit = len(comparison_table) == 1
            domain_ids = {'line'}
            k = 0
            for period in comparison_table:
                period_from = period[0]
                period_to = period[1]
                strict_range = False
                if line.special_date_changer == 'from_beginning':
                    period_from = False
                if line.special_date_changer == 'to_beginning_of_period':
                    date_tmp = datetime.strptime(period[0], "%Y-%m-%d") - relativedelta(days=1)
                    period_to = date_tmp.strftime('%Y-%m-%d')
                    period_from = False
                if line.special_date_changer == 'strict_range':
                    strict_range = True
                r = line.with_context(date_from=period_from, date_to=period_to, strict_range=strict_range)._eval_formula(financial_report, debit_credit, context, currency_table, linesDicts[k])
                debit_credit = False
                res.append(r)
                domain_ids.update(set(r.keys()))
                k += 1
            res = self._put_columns_together(res, domain_ids)
            if line.hide_if_zero and all([float_is_zero(k, precision_rounding=currency_precision) for k in res['line']]):
                continue

            # Post-processing ; creating line dictionnary, building comparison, computing total for extended, formatting
            vals = {
                'id': line.id,
                'name': line.name,
                'type': 'line',
                'level': line.level,
                'footnotes': context._get_footnotes('line', line.id),
                'columns': res['line'],
                'unfoldable': len(domain_ids) > 1 and line.show_domain != 'always',
                'unfolded': line in context.unfolded_lines or line.show_domain == 'always',
            }
            if line.action_id:
                vals['action_id'] = line.action_id.id
            domain_ids.remove('line')
            lines = [vals]
            groupby = line.groupby or 'aml'
            if line in context.unfolded_lines or line.show_domain == 'always':
                if line.groupby:
                    domain_ids = sorted(list(domain_ids), key=lambda k: line._get_gb_name(k))
                for domain_id in domain_ids:
                    name = line._get_gb_name(domain_id)
                    vals = {
                        'id': domain_id,
                        'name': name and len(name) >= 45 and name[0:40] + '...' or name,
                        'level': 1,
                        'type': groupby,
                        'footnotes': context._get_footnotes(groupby, domain_id),
                        'columns': res[domain_id],
                    }
                    if line.financial_report_id.name == 'Aged Receivable':
                        vals['trust'] = self.env['res.partner'].browse([domain_id]).trust
                    lines.append(vals)
                if domain_ids:
                    lines.append({
                        'id': line.id,
                        'name': _('Total') + ' ' + line.name,
                        'type': 'o_account_reports_domain_total',
                        'level': 1,
                        'footnotes': context._get_footnotes('o_account_reports_domain_total', line.id),
                        'columns': list(lines[0]['columns']),
                    })

            for vals in lines:
                # Adding forecast random value
                final_data = []
                for item in vals['columns']:
                    final_data.extend([random.randint(0,100) * 10, item])
                vals['columns'] = final_data
                if len(comparison_table) == 2:
                    vals['columns'].append(line._build_cmp(vals['columns'][0], vals['columns'][1]))
                    for i in [0, 1]:
                        vals['columns'][i] = line._format(vals['columns'][i])
                else:
                    vals['columns'] = map(line._format, vals['columns'])
                if not line.formulas:
                    vals['columns'] = ['' for k in vals['columns']]

            if len(lines) == 1:
                new_lines = line.children_ids.get_lines(financial_report, context, currency_table, linesDicts)
                if new_lines and line.level > 0 and line.formulas:
                    divided_lines = self._divide_line(lines[0])
                    result = [divided_lines[0]] + new_lines + [divided_lines[1]]
                else:
                    result = []
                    if line.level > 0:
                        result += lines
                    result += new_lines
                    if line.level <= 0:
                        result += lines
            else:
                result = lines
            final_result_table += result

        return final_result_table

AccountFinancialReportLine()