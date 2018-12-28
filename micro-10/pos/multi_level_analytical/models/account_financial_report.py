# -*- coding: utf-8 -*-
import ast
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime
from odoo.tools import float_is_zero
from dateutil.relativedelta import relativedelta

class AccountFinancialReportContext(models.TransientModel):
    _inherit = 'account.financial.html.report.context'

    analytic_level_id = fields.Many2one('account.analytic.level', string='Analytic Category')

    @api.multi
    def get_columns_names(self):
        columns = super(AccountFinancialReportContext, self).get_columns_names()
        # analytic_level_id = self.env.context.get('analytic_level_id')
        if self.analytic_level_id:
            analytic_account_ids = self.env['account.analytic.account'].search([('level_id','=',self.analytic_level_id.id)])
            if analytic_account_ids:
                columns = []
                for analytic in analytic_account_ids:
                    columns.append(analytic.name)
        return columns

    @api.multi
    def get_columns_types(self):
        result = super(AccountFinancialReportContext, self).get_columns_types()
        # analytic_level_id = self.env.context.get('analytic_level_id')
        if self.analytic_level_id:
            analytic_account_ids = self.env['account.analytic.account'].search([('level_id', '=', self.analytic_level_id.id)])
            if analytic_account_ids:
                result = ['number' for i in analytic_account_ids]
        return result

AccountFinancialReportContext()

class AccountFinancialReportLine(models.Model):
    _inherit = 'account.financial.html.report.line'

    def _process_formulas(self):
        result = self._split_formulas()
        if result:
            result = result.values()[0].split(' ')
        else:
            result = []
        result = filter(None, result)
        # checking -ve values
        final_result = []
        for item in result:
            if len(item) > 1 and '-' in item:
                final_result.append('-')
                final_result.append(item[1:])
            else:
                final_result.append(item)
        return final_result

    def _expand_formulas(self, formulas):
        # Temp value dict - This will be applied at end of calculation
        temp_value_dict = {'aaa': '', 'bbb': '', 'ccc': '', 'ddd': '', 'eee': ''}
        result = self._process_formulas()

        # Evaluate mixed formulas - formula contains Code and direct sum
        if 'sum.balance' in result:
            value = self.code + '.balance'
            for i in temp_value_dict:
                if not temp_value_dict.get(i):
                    temp_value_dict[i] = value
                    for count in range(0, len(result)):
                        if result[count] == 'sum.balance':
                            result[count] = i
                    break

        while 1:
            verify_list = []
            new_result = []
            for item in result:
                if len(item) > 1 and '.' in item:
                    data = item.split('.')
                    report_line_id = self.search([('code', '=', data[0])], limit=1)

                    check_flag = False
                    check_data = report_line_id._process_formulas()
                    for x in check_data:
                        if len(x) > 1 and ('.' in x):
                            check_data_split = x.split('.')
                            rec_id = self.search([('code', '=', check_data_split[0])], limit=1)
                            if rec_id:
                                check_flag = True
                                break

                    if not report_line_id.domain or check_flag:
                        data = report_line_id._process_formulas()
                        if any(operator in result for operator in ['+','-','*','/']) and any(operator in data for operator in ['+','-','*','/']):
                            new_data_list = ['(']
                            for item2 in data:
                                # Mixed formula calculation
                                if item2 == 'sum.balance':
                                    value = report_line_id.code + '.balance'
                                    for i in temp_value_dict:
                                        if not temp_value_dict.get(i):
                                            temp_value_dict[i] = value
                                            break
                                    new_data_list.append(i)
                                else:
                                    new_data_list.append(item2)
                            new_data_list.append(')')
                            new_result.extend(new_data_list)
                        else:
                            new_result.extend(data)
                        verify_list.append(False)
                    else:
                        new_result.append(item)
                        verify_list.append(True)
                else:
                    new_result.append(item)
                    verify_list.append(True)
                    operator = item
            result = new_result
            if all(verify_list):
                break

        # Applying temp values
        count = 0
        for x in result:
            if x in temp_value_dict:
                result[count] = temp_value_dict.get(x)
            count += 1
        return result

    def _eval_formula(self, financial_report, debit_credit, context, currency_table, linesDict):
        analytic_account_ids = self.env['account.analytic.account'].search([('level_id','=',context.analytic_level_id.id)]).ids
        analytic_amount_dict = dict([(id, 0.00) for id in analytic_account_ids])
        analytic_final_dict = dict([(id, '') for id in analytic_account_ids])

        check_flag = True
        check_data = self._process_formulas()
        for x in check_data:
            if len(x) > 1 and ('.' in x):
                check_data_split = x.split('.')
                rec_id = self.search([('code', '=', check_data_split[0])], limit=1)
                if rec_id:
                    check_flag = False
                    break

        account_ids = []
        if self.domain and check_flag:
            field_data = self.formulas.split(';')
            field_data = field_data[0].split('=')
            field_data = field_data[1].split('.')
            field_data_sign = field_data[0].replace('sum', '')

            domain = ast.literal_eval(self.domain)
            if self.env.context.get('date_from'):
                domain.extend([('date','>=',self.env.context.get('date_from'))])
            if self.env.context.get('date_to'):
                domain.extend([('date','<=',self.env.context.get('date_to'))])
            if context.analytic_manager_id.analytic_account_ids:
                domain.extend([('analytic_account_id','in',context.analytic_manager_id.analytic_account_ids.ids)])
            line_ids = self.env['account.move.line'].search(domain)
            for line in line_ids:
                account_ids.append(line.account_id.id)
                if line.analytic_account_id.id in analytic_amount_dict:
                    analytic_amount_dict.update({line.analytic_account_id.id: analytic_amount_dict.get(line.analytic_account_id.id) + line.read([field_data[1]])[0].get(field_data[1])})
            # Updating main dict
            for id in analytic_final_dict:
                analytic_final_dict[id] = field_data_sign + str(analytic_amount_dict.get(id))
        elif self.formulas:
            result = self._expand_formulas(self.formulas)
            for item in result:
                analytic_amount_dict = dict([(id, 0.00) for id in analytic_account_ids])
                if len(item) > 1:
                    if item == 'NDays':
                        # Updating main dict
                        d1 = datetime.strptime(self.env.context['date_from'], "%Y-%m-%d")
                        d2 = datetime.strptime(self.env.context['date_to'], "%Y-%m-%d")
                        days = (d2 - d1).days
                        for id in analytic_final_dict:
                            analytic_final_dict[id] = analytic_final_dict.get(id) + str(days)
                    else:
                        data = item.split('.')
                        report_line_id = self.search([('code', '=', data[0])], limit=1)
                        field_data = report_line_id.formulas.split(';')
                        field_data = field_data[0].split('=')
                        dot_count = report_line_id.formulas.count('.')
                        if dot_count == 1:
                            field_data = field_data[1].split('.')
                        else:
                            field_data = field_data[1].split(' ')
                            new_field_data = []
                            for x in field_data:
                                if 'sum' in x:
                                    new_field_data.append(x)
                            field_data = new_field_data[0].split('.')
                        field_data_sign = field_data[0].replace('sum', '')

                        domain = ast.literal_eval(report_line_id.domain)
                        if self.env.context.get('date_from'):
                            domain.extend([('date', '>=', self.env.context.get('date_from'))])
                        if self.env.context.get('date_to'):
                            domain.extend([('date', '<=', self.env.context.get('date_to'))])
                        if context.analytic_manager_id.analytic_account_ids:
                            domain.extend([('analytic_account_id','in',context.analytic_manager_id.analytic_account_ids.ids)])
                        line_ids = self.env['account.move.line'].search(domain)
                        for line in line_ids:
                            account_ids.append(line.account_id.id)
                            if line.analytic_account_id.id in analytic_amount_dict:
                                analytic_amount_dict[line.analytic_account_id.id] = analytic_amount_dict.get(line.analytic_account_id.id) + line.read([field_data[1]])[0].get(field_data[1])
                        # Updating main dict
                        for id in analytic_amount_dict:
                            analytic_final_dict[id] = analytic_final_dict.get(id) + field_data_sign + str(analytic_amount_dict.get(id))

                elif item == 'NDays':
                    # Updating main dict
                    d1 = datetime.strptime(self.env.context['date_from'], "%Y-%m-%d")
                    d2 = datetime.strptime(self.env.context['date_to'], "%Y-%m-%d")
                    days = (d2 - d1).days
                    for id in analytic_final_dict:
                        analytic_final_dict[id] = analytic_final_dict.get(id) + str(days)
                else:
                    # Updating main dict
                    for id in analytic_final_dict:
                        analytic_final_dict[id] = analytic_final_dict.get(id) + item

        debit_credit = debit_credit and financial_report.debit_credit
        formulas = self._split_formulas()
        if self.code and self.code in linesDict:
            res = linesDict[self.code]
        else:
            res = FormulaLine(self, currency_table, financial_report, linesDict=linesDict)
        vals = {}
        vals['balance'] = res.balance
        vals['account_ids'] = list(set(account_ids))
        if context.analytic_level_id:
            vals['analytic_final_dict'] = analytic_final_dict
        if debit_credit:
            vals['credit'] = res.credit
            vals['debit'] = res.debit

        results = {}
        if self.domain and self.groupby and self.show_domain != 'never':
            aml_obj = self.env['account.move.line']
            tables, where_clause, where_params = aml_obj._query_get(domain=self.domain)
            sql, params = self._get_with_statement(financial_report)
            if financial_report.tax_report:
                where_clause += ''' AND "account_move_line".tax_exigible = 't' '''

            groupby = self.groupby or 'id'
            if groupby not in self.env['account.move.line']:
                raise ValueError('Groupby should be a field from account.move.line')
            select, select_params = self._query_get_select_sum(currency_table)
            params += select_params
            sql = sql + "SELECT \"account_move_line\"." + groupby + ", " + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY \"account_move_line\"." + groupby

            params += where_params
            self.env.cr.execute(sql, params)
            results = self.env.cr.fetchall()
            results = dict([(k[0], {'balance': k[1], 'amount_residual': k[2], 'debit': k[3], 'credit': k[4]}) for k in results])
            c = FormulaContext(self.env['account.financial.html.report.line'], linesDict, currency_table, financial_report, only_sum=True)
            if formulas:
                for key in results:
                    c['sum'] = FormulaLine(results[key], currency_table, financial_report, type='not_computed')
                    c['sum_if_pos'] = FormulaLine(results[key]['balance'] >= 0.0 and results[key] or {'balance': 0.0}, currency_table, financial_report, type='not_computed')
                    c['sum_if_neg'] = FormulaLine(results[key]['balance'] <= 0.0 and results[key] or {'balance': 0.0}, currency_table, financial_report, type='not_computed')
                    for col, formula in formulas.items():
                        if col in results[key]:
                            results[key][col] = safe_eval(formula, c, nocopy=True)
            to_del = []
            for key in results:
                if self.env.user.company_id.currency_id.is_zero(results[key]['balance']):
                    to_del.append(key)
            for key in to_del:
                del results[key]

        results.update({'line': vals})
        return results

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
            res.update({'account_ids': r['line'].get('account_ids')})
            if r['line'].get('analytic_final_dict'):
                res.update({'analytic_final_dict': r['line'].get('analytic_final_dict')})

            if line.hide_if_zero and all([float_is_zero(k, precision_rounding=currency_precision) for k in res['line']]):
                continue

            # Analytic level based amount
            columns = []
            if context.analytic_level_id and res.get('analytic_final_dict'):
                analytic_account_ids = self.env['account.analytic.account'].search([('level_id', '=', context.analytic_level_id.id)]).ids
                for aa_id in analytic_account_ids:
                    amount_string = res.get('analytic_final_dict').get(aa_id)
                    try:
                        amount = amount_string and eval(amount_string) or 0.0
                    except:
                        amount = 0.0
                    columns.append(amount)
            if not columns:
                columns = res['line']

            # Post-processing ; creating line dictionnary, building comparison, computing total for extended, formatting
            vals = {
                'id': line.id,
                'name': line.name,
                'type': 'line',
                'level': line.level,
                'footnotes': context._get_footnotes('line', line.id),
                'columns': columns,
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
                if len(comparison_table) == 2:
                    vals['columns'].append(line._build_cmp(vals['columns'][0], vals['columns'][1]))
                    for i in [0, 1]:
                        vals['columns'][i] = line._format(vals['columns'][i])
                else:
                    vals['columns'] = map(line._format, vals['columns'])
                    domain_list = [('move_id.state','=','posted'),('account_id','=',vals.get('id'))]
                    if context.date_from:
                        domain_list.append(('date','>=',context.date_from))
                    if context.date_to:
                        domain_list.append(('date','<=',context.date_to))
                    if (vals.get('type') == 'account_id') and context.analytic_level_id:
                        columns = []
                        analytic_account_ids = self.env['account.analytic.account'].search([('level_id','=',context.analytic_level_id.id)]).ids
                        for aa_id in analytic_account_ids:
                            move_ids = self.env['account.move.line'].search(domain_list + [('analytic_account_id','=',aa_id)])
                            amount = 0.0
                            for move in move_ids:
                                amount += move.balance
                            columns.append(abs(amount))
                    if (vals.get('type') == 'account_id') and not context.analytic_level_id:
                        columns = []
                        move_ids = self.env['account.move.line'].search(domain_list)
                        amount = 0.0
                        for move in move_ids:
                            amount += move.balance
                        columns.append(abs(amount))
                    if (vals.get('type') == 'o_account_reports_domain_total') and context.analytic_level_id:
                        columns = []
                        analytic_account_ids = self.env['account.analytic.account'].search([('level_id', '=', context.analytic_level_id.id)]).ids
                        for aa_id in analytic_account_ids:
                            amount = 0.0
                            domain_list = [('move_id.state', '=', 'posted'),('analytic_account_id','=',aa_id)]
                            if context.date_from:
                                domain_list.append(('date', '>=', context.date_from))
                            if context.date_to:
                                domain_list.append(('date', '<=', context.date_to))
                            for account_id in res.get('account_ids', []):
                                move_ids = self.env['account.move.line'].search(domain_list + [('account_id','=',account_id)])
                                for move in move_ids:
                                    amount += move.balance
                            columns.append(abs(amount))
                    if (vals.get('type') == 'o_account_reports_domain_total') and not context.analytic_level_id:
                        columns = []
                        amount = 0.0
                        domain_list = [('move_id.state', '=', 'posted')]
                        if context.date_from:
                            domain_list.append(('date', '>=', context.date_from))
                        if context.date_to:
                            domain_list.append(('date', '<=', context.date_to))
                        for account_id in res.get('account_ids', []):
                            move_ids = self.env['account.move.line'].search(domain_list + [('account_id', '=', account_id)])
                            for move in move_ids:
                                amount += move.balance
                        columns.append(abs(amount))
                    if columns:
                        vals['columns'] = map(line._format, columns)
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

class FormulaLine(object):
    def __init__(self, obj, currency_table, financial_report, type='balance', linesDict=None):
        if linesDict is None:
            linesDict = {}
        fields = dict((fn, 0.0) for fn in ['debit', 'credit', 'balance'])
        if type == 'balance':
            fields = obj.get_balance(linesDict, currency_table, financial_report)[0]
            linesDict[obj.code] = self
        elif type in ['sum', 'sum_if_pos', 'sum_if_neg']:
            if type == 'sum_if_neg':
                obj = obj.with_context(sum_if_neg=True)
            if type == 'sum_if_pos':
                obj = obj.with_context(sum_if_pos=True)
            if obj._name == 'account.financial.html.report.line':
                fields = obj._get_sum(currency_table, financial_report)
                self.amount_residual = fields['amount_residual']
            elif obj._name == 'account.move.line':
                self.amount_residual = 0.0
                field_names = ['debit', 'credit', 'balance', 'amount_residual']
                res = obj.env['account.financial.html.report.line']._compute_line(currency_table, financial_report)
                for field in field_names:
                    fields[field] = res[field]
                self.amount_residual = fields['amount_residual']
        elif type == 'not_computed':
            for field in fields:
                fields[field] = obj.get(field, 0)
            self.amount_residual = obj.get('amount_residual', 0)
        elif type == 'null':
            self.amount_residual = 0.0
        self.balance = fields['balance']
        self.credit = fields['credit']
        self.debit = fields['debit']

class FormulaContext(dict):
    def __init__(self, reportLineObj, linesDict, currency_table, financial_report, curObj=None, only_sum=False, *data):
        self.reportLineObj = reportLineObj
        self.curObj = curObj
        self.linesDict = linesDict
        self.currency_table = currency_table
        self.only_sum = only_sum
        self.financial_report = financial_report
        return super(FormulaContext, self).__init__(data)

    def __getitem__(self, item):
        formula_items = ['sum', 'sum_if_pos', 'sum_if_neg']
        if item in set(__builtins__.keys()) - set(formula_items):
            return super(FormulaContext, self).__getitem__(item)

        if self.only_sum and item not in formula_items:
            return FormulaLine(self.curObj, self.currency_table, self.financial_report, type='null')
        if self.get(item):
            return super(FormulaContext, self).__getitem__(item)
        if self.linesDict.get(item):
            return self.linesDict[item]
        if item == 'sum':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum')
            self['sum'] = res
            return res
        if item == 'sum_if_pos':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum_if_pos')
            self['sum_if_pos'] = res
            return res
        if item == 'sum_if_neg':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum_if_neg')
            self['sum_if_neg'] = res
            return res
        if item == 'NDays':
            d1 = datetime.strptime(self.curObj.env.context['date_from'], "%Y-%m-%d")
            d2 = datetime.strptime(self.curObj.env.context['date_to'], "%Y-%m-%d")
            res = (d2 - d1).days
            self['NDays'] = res
            return res
        line_id = self.reportLineObj.search([('code', '=', item)], limit=1)
        if line_id:
            strict_range = line_id.special_date_changer == 'strict_range'
            period_from = line_id._context['date_from']
            period_to = line_id._context['date_to']
            if line_id.special_date_changer == 'from_beginning':
                period_from = False
            if line_id.special_date_changer == 'to_beginning_of_period' and line_id._context.get('date_from'):
                date_tmp = datetime.strptime(line_id._context['date_from'], "%Y-%m-%d") - relativedelta(days=1)
                period_to = date_tmp.strftime('%Y-%m-%d')
                period_from = False
            res = FormulaLine(line_id.with_context(strict_range=strict_range, date_from=period_from, date_to=period_to), self.currency_table, self.financial_report, linesDict=self.linesDict)
            self.linesDict[item] = res
            return res
        return super(FormulaContext, self).__getitem__(item)
