# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, api, _, fields
from odoo.tools.misc import formatLang
import time
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DTF

class ReportAgedPartnerBalance(models.AbstractModel):
    _inherit = 'report.account.report_agedpartnerbalance'

    def _get_partner_move_lines2(self, account_type, date_from, target_move, period_length, target_domain):
        report_date_query = '(l.date <= %s)'
        # if self.env.context.get('aging_due_filter_cmp'):
        #     report_date_query = '(l.date_maturity <= %s)'

        periods = {}
        start = datetime.strptime(date_from, "%Y-%m-%d")
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            periods[str(i)] = {
                'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        res = []
        total = []
        cr = self.env.cr
        user_company = self.env.user.company_id.id
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type))
        #build the reconciliation clause to see what partner needs to be printed
        reconciliation_clause = '(l.reconciled IS FALSE)'
        cr.execute('SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where create_date > %s', (date_from,))
        reconciled_after_date = []
        for row in cr.fetchall():
            reconciled_after_date += [row[0], row[1]]
        if reconciled_after_date:
            reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
            arg_list += (tuple(reconciled_after_date),)
        arg_list += (date_from, user_company)
        query = '''
            SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
            FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.internal_type IN %s)
                AND ''' + reconciliation_clause + '''
                AND ''' + report_date_query + '''
                AND l.company_id = %s
                AND l.invoice_id is not NULL
                AND (SELECT state FROM account_invoice WHERE id = l.invoice_id) = 'open'
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], []

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        rate_dict = {}
        currency_dict = {}
        if target_domain:
            query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (SELECT currency_id FROM account_invoice WHERE id = l.invoice_id) in %s
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) > %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND ''' + report_date_query + '''
                AND l.company_id = %s
                AND l.invoice_id is not NULL
                AND (SELECT state FROM account_invoice WHERE id = l.invoice_id) = 'open'
                '''
            cr.execute(query, (tuple(move_state),tuple(target_domain), tuple(account_type), date_from, tuple(partner_ids), date_from, user_company))
        else:
            query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) > %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND ''' + report_date_query + '''
                AND l.company_id = %s
                AND l.invoice_id is not NULL
                AND (SELECT state FROM account_invoice WHERE id = l.invoice_id) = 'open'
                '''
            cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, user_company))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            line_amount = line.balance
            if line.balance == 0:
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.create_date[:10] <= date_from:
                    line_amount += partial_line.amount
            for partial_line in line.matched_credit_ids:
                if partial_line.create_date[:10] <= date_from:
                    line_amount -= partial_line.amount
            if not self.env.user.company_id.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                if line.move_id:
                    currency = self.env['account.invoice'].search([('number','=',line.move_id.name)],limit=1).currency_id
                    currency_dict[partner_id] = currency.name
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 5,
                    'main_period': 0,
                    'amount_currency': abs(line.amount_currency) or line_amount,
                    'amount_residual': abs(line.amount_residual) or line_amount,
                })

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, user_company)
            if target_domain:
                query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND ''' + report_date_query + '''
                    AND l.company_id = %s
                    AND (SELECT currency_id FROM account_invoice WHERE id = l.invoice_id) in %s
                    AND l.invoice_id is not NULL
                    AND (SELECT state FROM account_invoice WHERE id = l.invoice_id) = 'open'
                    '''
                args_list += (tuple(target_domain),)
            else:
                query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND ''' + report_date_query + '''
                    AND l.company_id = %s
                    AND l.invoice_id is not NULL
                    AND (SELECT state FROM account_invoice WHERE id = l.invoice_id) = 'open'
                    '''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                line_amount = line.balance
                if line.balance == 0:
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.create_date[:10] <= date_from:
                        line_amount += partial_line.amount
                for partial_line in line.matched_credit_ids:
                    if partial_line.create_date[:10] <= date_from:
                        line_amount -= partial_line.amount

                if not self.env.user.company_id.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i,
                        'amount_currency': abs(line.amount_currency) or line_amount,
                        'amount_residual': abs(line.amount_residual) or line_amount,
                    })
            history.append(partners_amount)

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]
            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt

            if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
            ## Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount:
                res.append(values)
        return res, total, lines

class report_account_aged_partner(models.AbstractModel):
    _name = "account.aged.partner"
    _description = "Aged Partner Balances"

    def _format(self, value):
        if self.env.context.get('no_format'):
            return value
        currency_id = self.env.user.company_id.currency_id
        if currency_id.is_zero(value):
            value = abs(value)
        return formatLang(self.env, value)

    @api.model
    def _lines(self, context, line_id=None):
        sign = 1.0
        lines = []
        multi_currency = False
        currency_ids = self._context.get('currency_ids',[])
        results, total, amls = self.env['report.account.report_agedpartnerbalance']._get_partner_move_lines2([self._context['account_type']], self._context['date_to'], 'posted', 30, currency_ids)
        config_setting = self.env['account.config.settings'].search([],order='id desc', limit=1)
        if config_setting and config_setting.group_multi_currency:
            multi_currency = True

        # Calculate invoice currency amount total
        partner_currency_total = {}
        partner_residual_total = {}

        partner_ids = []
        for line in results:
            partner_ids.append(line.get('partner_id'))
        partner_ids = list(set(partner_ids))

        for partner_id in amls:
            if partner_id in partner_ids:
                for line in amls.get(partner_id):
                    aml = line['line']
                    invoice = self.env['account.invoice'].search([('number', '=', aml.move_id.name)], limit=1)
                    currency_id = invoice.currency_id or self.env.user.company_id.currency_id
                    if invoice:
                        currency_rate = invoice.with_context(date=invoice.date_invoice).currency_id.rate
                    else:
                        currency_rate = currency_id.rate
                    invoice_sign = 1.0
                    if invoice.type in ('out_refund', 'in_refund'):
                        invoice_sign = -1.0
                    # Currency Total
                    if partner_id not in partner_currency_total:
                        partner_currency_total.update({partner_id: round(invoice_sign * abs(line.get('amount_currency')), 2)})
                    else:
                        partner_currency_total.update({partner_id: partner_currency_total.get(partner_id) + round(invoice_sign * abs(line.get('amount_currency')), 2)})
                    # Residual Total
                    if self.env.context.get('filter_original_currency'):
                        if partner_id not in partner_residual_total:
                            partner_residual_total.update({partner_id: round(invoice.residual_signed or line['amount'], 2)})
                        else:
                            partner_residual_total.update({partner_id: partner_residual_total.get(partner_id) + round(invoice.residual_signed or line['amount'], 2)})
                    else:
                        if partner_id not in partner_residual_total:
                            partner_residual_total.update({partner_id: round(float(invoice.residual_signed or line['amount']) / float(currency_rate), 2)})
                        else:
                            partner_residual_total.update({partner_id: partner_residual_total.get(partner_id) + round((float(invoice.residual_signed or line['amount']) / float(currency_rate)), 2)})

        # Not due invoices
        partner_not_due_dict = {}
        partner_totals = {}
        partner_totals_final = {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00}
        overall_due_current_total = 0.00
        current_date = datetime.strptime(self._context['date_to'], "%Y-%m-%d")
        for values in results:
            # Not due invoices
            domain = [('partner_id','=',values['partner_id']),('date_due','>',self.env.context.get('date_to')),('date_invoice','<=',self.env.context.get('date_to')),('state','=','open')]
            invoice_ids = self.env['account.invoice'].search(domain)
            partner_not_due_dict.update({values['partner_id']: 0.00})
            for invoice in invoice_ids:
                partner_not_due_dict.update({values['partner_id']: partner_not_due_dict.get(values['partner_id']) + invoice.residual_signed})

            # Total per period
            partner_totals.update({values['partner_id']: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00}})
            for line in amls[values['partner_id']]:
                aml = line['line']
                invoice = self.env['account.invoice'].search([('number', '=', aml.move_id.name)], limit=1)
                currency_id = invoice.currency_id or self.env.user.company_id.currency_id
                invoice_sign = 1.0
                if invoice.type in ('out_refund', 'in_refund'):
                    invoice_sign = -1.0
                if invoice:
                    currency_rate = invoice.with_context(date=invoice.date_invoice).currency_id.rate
                else:
                    currency_rate = currency_id.rate
                age = current_date - current_date
                if self.env.context.get('aging_due_filter_cmp'):
                    if invoice.date_due:
                        age = current_date - datetime.strptime(invoice.date_due, "%Y-%m-%d")
                elif invoice.date_invoice:
                    age = current_date - datetime.strptime(invoice.date_invoice, "%Y-%m-%d")

                # 0-30 days
                if age.days >= 0 and age.days <= 30:
                    amount = partner_totals.get(values['partner_id']).get(0)
                    if self.env.context.get('filter_original_currency'):
                        partner_totals.get(values['partner_id']).update({0: amount + (invoice_sign * abs(line['amount_currency']))})
                        partner_totals_final.update({0: partner_totals_final.get(0) + (invoice_sign * abs(line['amount_currency']))})
                    else:
                        partner_totals.get(values['partner_id']).update({0: amount + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})
                        partner_totals_final.update({0: partner_totals_final.get(0) + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})
                # 30-60 days
                if age.days >= 31 and age.days <= 60:
                    amount = partner_totals.get(values['partner_id']).get(1)
                    if self.env.context.get('filter_original_currency'):
                        partner_totals.get(values['partner_id']).update({1: amount + (invoice_sign * abs(line['amount_currency']))})
                        partner_totals_final.update({1: partner_totals_final.get(1) + (invoice_sign * abs(line['amount_currency']))})
                    else:
                        partner_totals.get(values['partner_id']).update({1: amount + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})
                        partner_totals_final.update({1: partner_totals_final.get(1) + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})
                # 60-90 days
                if age.days >= 61 and age.days <= 90:
                    amount = partner_totals.get(values['partner_id']).get(2)
                    if self.env.context.get('filter_original_currency'):
                        partner_totals.get(values['partner_id']).update({2: amount + (invoice_sign * abs(line['amount_currency']))})
                        partner_totals_final.update({2: partner_totals_final.get(2) + (invoice_sign * abs(line['amount_currency']))})
                    else:
                        partner_totals.get(values['partner_id']).update({2: amount + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})
                        partner_totals_final.update({2: partner_totals_final.get(2) + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})
                # 90-120 days
                if age.days >= 91 and age.days <= 120:
                    amount = partner_totals.get(values['partner_id']).get(3)
                    if self.env.context.get('filter_original_currency'):
                        partner_totals.get(values['partner_id']).update({3: amount + (invoice_sign * abs(line['amount_currency']))})
                        partner_totals_final.update({3: partner_totals_final.get(3) + (invoice_sign * abs(line['amount_currency']))})
                    else:
                        partner_totals.get(values['partner_id']).update({3: amount + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})
                        partner_totals_final.update({3: partner_totals_final.get(3) + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})
                # >120 days
                if age.days > 120:
                    amount = partner_totals.get(values['partner_id']).get(4)
                    if self.env.context.get('filter_original_currency'):
                        partner_totals.get(values['partner_id']).update({4: amount + (invoice_sign * abs(line['amount_currency']))})
                        partner_totals_final.update({4: partner_totals_final.get(4) + (invoice_sign * abs(line['amount_currency']))})
                    else:
                        partner_totals.get(values['partner_id']).update({4: amount + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})
                        partner_totals_final.update({4: partner_totals_final.get(4) + (invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate)))})

        for values in results:
            partner_total_line = partner_totals.get(values['partner_id'])
            columns = [partner_total_line[0], partner_total_line[1], partner_total_line[2], partner_total_line[3], partner_total_line[4]]
            if self.env.context.get('aging_due_filter_cmp'):
                columns = [partner_not_due_dict.get(values['partner_id']), partner_total_line[0], partner_total_line[1], partner_total_line[2], partner_total_line[3] + partner_total_line[4]]

            if line_id and values['partner_id'] != line_id:
                continue
            customer = self.env['res.partner'].browse(values['partner_id'])
            vals = {
                'id': values['partner_id'] and values['partner_id'] or -1,
                'name': values['name'],
                'customer_id':customer.customer_id,
                'level': 0 if values['partner_id'] else 2,
                'type': values['partner_id'] and 'partner_id' or 'line',
                'footnotes': context._get_footnotes('partner_id', values['partner_id']),
                'columns': columns,
                'multi_currency':multi_currency,
                'trust': values['trust'],
                'unfoldable': values['partner_id'] and True or False,
                'unfolded': values['partner_id'] and (values['partner_id'] in context.unfolded_partners.ids) or False,
            }
            vals['columns'] = [self._format(t) for t in vals['columns']]
            if self.env.context.get('filter_original_currency'):
                vals['columns'].extend([self._format(sign * partner_currency_total.get(values['partner_id']))])
                vals['columns'].extend([self._format(sign * partner_currency_total.get(values['partner_id'])), ''])
            else:
                vals['columns'].extend([self._format(partner_residual_total.get(values['partner_id']))])
                vals['columns'].extend([self._format(sign * partner_currency_total.get(values['partner_id'])), ''])
            if self.env.context.get('filter_local_currency') or self.env.context.get('filter_original_currency'):
                vals['columns'].extend(['',''])
            lines.append(vals)
            partner_due_current_total = 0.00
            if values['partner_id'] in context.unfolded_partners.ids:
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    vals = {
                        'id': aml.id,
                        'name': aml.move_id.name if aml.move_id.name else '/',
                        'move_id': aml.move_id.id,
                        'partnerid':values['partner_id'],
                        'action': aml.get_model_id_and_name(),
                        'multi_currency':multi_currency,
                        'level': 1,
                        'type': 'move_line_id',
                        'footnotes': context._get_footnotes('move_line_id', aml.id),
                    }

                    invoice = self.env['account.invoice'].search([('number','=',aml.move_id.name)],limit=1)
                    currency_id = invoice.currency_id or self.env.user.company_id.currency_id
                    if invoice:
                        currency_rate = invoice.with_context(date=invoice.date_invoice).currency_id.rate
                    else:
                        currency_rate = currency_id.rate
                    invoice_sign = 1.0
                    if invoice.type in ('out_refund', 'in_refund'):
                        invoice_sign = -1.0
                    age = current_date - current_date
                    if self.env.context.get('aging_due_filter_cmp'):
                        if invoice.date_due:
                            age = current_date - datetime.strptime(invoice.date_due, "%Y-%m-%d")
                    elif invoice.date_invoice:
                        age = current_date - datetime.strptime(invoice.date_invoice, "%Y-%m-%d")

                    # Calculating period based amount
                    if self.env.context.get('aging_due_filter_cmp'):
                        if invoice.date_due:
                            cmp_date_due = datetime.strptime(invoice.date_due, "%Y-%m-%d")
                            if cmp_date_due <= current_date:
                                final_columns = ['']
                                due_date = current_date
                                report_date = datetime.strptime(self.env.context.get('date_to'), "%Y-%m-%d")
                                if invoice.date_due:
                                    due_date = datetime.strptime(invoice.date_due, "%Y-%m-%d")
                                # 0-30 days
                                if (age.days >= 0 and age.days <= 30) or (due_date > report_date):
                                    if self.env.context.get('filter_original_currency'):
                                        final_columns.append(self._format(invoice_sign * abs(line['amount_currency'])))
                                    else:
                                        final_columns.append(self._format(invoice_sign * ((float(invoice.residual or abs(line['amount'])) / float(currency_rate)))))
                                else:
                                    final_columns.append('')
                                # 30-60 days
                                if age.days >= 31 and age.days <= 60 and due_date <= report_date:
                                    if self.env.context.get('filter_original_currency'):
                                        final_columns.append(self._format(invoice_sign * abs(line['amount_currency'])))
                                    else:
                                        final_columns.append(self._format(invoice_sign * ((float(invoice.residual or abs(line['amount'])) / float(currency_rate)))))
                                else:
                                    final_columns.append('')
                                # 60-90 days
                                if age.days >= 61 and age.days <= 90 and due_date <= report_date:
                                    if self.env.context.get('filter_original_currency'):
                                        final_columns.append(self._format(invoice_sign * abs(line['amount_currency'])))
                                    else:
                                        final_columns.append(self._format(invoice_sign * ((float(invoice.residual or abs(line['amount'])) / float(currency_rate)))))
                                else:
                                    final_columns.append('')
                                # >90 days
                                if age.days > 90 and due_date <= report_date:
                                    if self.env.context.get('filter_original_currency'):
                                        final_columns.append(self._format(invoice_sign * abs(line['amount_currency'])))
                                    else:
                                        final_columns.append(self._format(invoice_sign * ((float(invoice.residual or abs(line['amount'])) / float(currency_rate)))))
                                else:
                                    final_columns.append('')
                    else:
                        final_columns = []
                        # 0-30 days
                        if age.days >= 0 and age.days <= 30:
                            if self.env.context.get('filter_original_currency'):
                                final_columns.append(self._format(invoice_sign * abs(line['amount_currency'])))
                            else:
                                final_columns.append(self._format(invoice_sign * ((float(invoice.residual or abs(line['amount'])) / float(currency_rate)))))
                        else:
                            final_columns.append('')
                        # 30-60 days
                        if age.days >= 31 and age.days <= 60:
                            if self.env.context.get('filter_original_currency'):
                                final_columns.append(self._format(invoice_sign * abs(line['amount_currency'])))
                            else:
                                final_columns.append(self._format(invoice_sign * ((float(invoice.residual or abs(line['amount'])) / float(currency_rate)))))
                        else:
                            final_columns.append('')
                        # 60-90 days
                        if age.days >= 61 and age.days <= 90:
                            if self.env.context.get('filter_original_currency'):
                                final_columns.append(self._format(invoice_sign * abs(line['amount_currency'])))
                            else:
                                final_columns.append(self._format(invoice_sign * ((float(invoice.residual or abs(line['amount'])) / float(currency_rate)))))
                        else:
                            final_columns.append('')
                        # 90-120 days
                        if age.days >= 91 and age.days <= 120:
                            if self.env.context.get('filter_original_currency'):
                                final_columns.append(self._format(invoice_sign * abs(line['amount_currency'])))
                            else:
                                final_columns.append(self._format(invoice_sign * ((float(invoice.residual or abs(line['amount'])) / float(currency_rate)))))
                        else:
                            final_columns.append('')
                        # >120 days
                        if age.days > 120:
                            if self.env.context.get('filter_original_currency'):
                                final_columns.append(self._format(invoice_sign * abs(line['amount_currency'])))
                            else:
                                final_columns.append(self._format(invoice_sign * ((float(invoice.residual or abs(line['amount'])) / float(currency_rate)))))
                        else:
                            final_columns.append('')

                    # Update total
                    invoice_date = invoice.date_invoice and datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%d-%m-%Y')
                    due_date = invoice.date_due and datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime('%d-%m-%Y')
                    if due_date:
                        cmp_date_due = datetime.strptime(invoice.date_due, "%Y-%m-%d")

                    if (not self.env.context.get('aging_due_filter_cmp')) or (due_date and (cmp_date_due <= current_date)):
                        vals['columns'] = [invoice_date, due_date]
                        vals['columns'].extend(final_columns)
                        if self.env.context.get('filter_original_currency'):
                            vals['columns'].extend([self._format(invoice_sign * abs(line['amount_currency'])) or ''])
                            vals['columns'].extend([self._format(invoice_sign * abs(line['amount_currency'])) or ''])
                        else:
                            vals['columns'].extend([self._format(invoice_sign * (float(invoice.residual or abs(line['amount'])) / float(currency_rate))) or ''])
                            vals['columns'].extend([self._format(invoice_sign * abs(line['amount_currency'])) or ''])
                        vals['columns'].extend([(age.days if age.days > 0 else '0')])
                        if self.env.context.get('filter_local_currency') or self.env.context.get('filter_original_currency'):
                            vals['columns'].extend([invoice.currency_id.name or '', "%.2f" % (currency_rate or 0.0)])
                        lines.append(vals)

                if self.env.context.get('aging_due_filter_cmp'):
                    domain = [('partner_id','=',values['partner_id']),('date_due','>',self.env.context.get('date_to')),('date_invoice','<=',self.env.context.get('date_to')),('state','=','open')]
                    invoice_ids = self.env['account.invoice'].search(domain)
                    for invoice in invoice_ids:
                        currency_rate = invoice.with_context(date=invoice.date_invoice).currency_id.rate
                        invoice_sign = 1
                        if invoice.type in ('out_refund', 'in_refund'):
                            invoice_sign = -1
                        vals = {
                            'id': invoice.move_id.id,
                            'name': invoice.number or '/',
                            'move_id': invoice.move_id.id,
                            'partnerid': values['partner_id'],
                            'action': invoice.move_id.line_ids[0].get_model_id_and_name(),
                            'multi_currency': multi_currency,
                            'level': 1,
                            'type': 'move_line_id',
                            'footnotes': context._get_footnotes('move_line_id', invoice.move_id.id),
                        }

                        invoice_date = invoice.date_invoice and datetime.strptime(invoice.date_invoice, '%Y-%m-%d').strftime('%d-%m-%Y')
                        due_date = invoice.date_due and datetime.strptime(invoice.date_due, '%Y-%m-%d').strftime('%d-%m-%Y')
                        age = current_date - current_date
                        if self.env.context.get('aging_due_filter_cmp'):
                            if invoice.date_due:
                                age = current_date - datetime.strptime(invoice.date_due, "%Y-%m-%d")
                        elif invoice.date_invoice:
                            age = current_date - datetime.strptime(invoice.date_invoice, "%Y-%m-%d")

                        vals['columns'] = [invoice_date, due_date]
                        vals['columns'].extend([self._format(invoice_sign * invoice.amount_total),'','','',''])
                        if self.env.context.get('filter_original_currency'):
                            vals['columns'].extend([self._format(invoice_sign * invoice.amount_total) or ''])
                            vals['columns'].extend([self._format(invoice_sign * invoice.amount_total) or ''])
                        else:
                            vals['columns'].extend([self._format(invoice_sign * (float(invoice.residual) / float(currency_rate))) or ''])
                            vals['columns'].extend([self._format(invoice_sign * invoice.amount_total) or ''])
                        vals['columns'].extend([(age.days if age.days > 0 else '0')])
                        with_ctx_currency = invoice.company_id.currency_id.with_context(date=invoice.date_invoice)
                        if self.env.context.get('filter_local_currency') or self.env.context.get('filter_original_currency'):
                            vals['columns'].extend([invoice.currency_id.name or '', "%.2f" % (currency_rate or 0.0)])
                        lines.append(vals)

                partner_total_line = partner_totals.get(values['partner_id'])
                columns = [partner_total_line[0], partner_total_line[1], partner_total_line[2], partner_total_line[3], partner_total_line[4]]
                if self.env.context.get('aging_due_filter_cmp'):
                    columns = [partner_not_due_dict.get(values['partner_id']), partner_total_line[0], partner_total_line[1], partner_total_line[2], partner_total_line[3] + partner_total_line[4]]

                vals1 = {
                    'id': values['partner_id'],
                    'type': 'o_account_reports_domain_total',
                    'name': _('Total'),
                    'footnotes': self.env.context['context_id']._get_footnotes('o_account_reports_domain_total', values['partner_id']),
                    'columns': columns,
                    'level': 1,
                }
                final_columns1 = [self._format(t) for t in vals1['columns']]
                vals1['columns'] = ['', '']
                vals1['columns'].extend(final_columns1)
                if self.env.context.get('filter_original_currency'):
                    vals1['columns'].extend([self._format(sign * partner_currency_total.get(values['partner_id']))])
                    vals1['columns'].extend([self._format(sign * partner_currency_total.get(values['partner_id'])), ''])
                else:
                    vals1['columns'].extend([self._format(sign * partner_residual_total.get(values['partner_id']))])
                    vals1['columns'].extend([self._format(sign * partner_currency_total.get(values['partner_id'])), ''])
                if self.env.context.get('filter_local_currency') or self.env.context.get('filter_original_currency'):
                    vals1['columns'].extend(['',''])
                lines.append(vals1)
            # Updating overall total for current / not due amount
            overall_due_current_total += partner_residual_total.get(values['partner_id'])

        if total and not line_id:
            currency_total = sum(partner_currency_total.values())
            columns = [partner_totals_final[0], partner_totals_final[1], partner_totals_final[2], partner_totals_final[3], partner_totals_final[4]]
            if self.env.context.get('aging_due_filter_cmp'):
                columns = [sum(partner_not_due_dict.values()), partner_totals_final[0], partner_totals_final[1], partner_totals_final[2], partner_totals_final[3] + partner_totals_final[4]]

            total_line = {
                'id': 0,
                'name': _('Total'),
                'level': 0,
                'multi_currency':multi_currency,
                'type': 'o_account_reports_domain_total',
                'footnotes': context._get_footnotes('o_account_reports_domain_total', 0),
                'columns': columns,
            }
            final_columns = [self._format(t) for t in total_line['columns']]
            total_line['columns'] = ['', '']
            total_line['columns'].extend(final_columns)
            if self.env.context.get('filter_original_currency'):
                total_line['columns'].extend([self._format(sign * currency_total)])
                total_line['columns'].extend([self._format(sign * currency_total), ''])
            else:
                total_line['columns'].extend([self._format(sign * sum([float("%.2f" % x) for x in partner_residual_total.values()]))])
                total_line['columns'].extend([self._format(sign * currency_total), ''])
            if self.env.context.get('filter_local_currency') or self.env.context.get('filter_original_currency'):
                total_line['columns'].extend(['',''])
            lines.append(total_line)
        return lines

class report_account_aged_receivable(models.AbstractModel):
    _name = "account.aged.receivable"
    _description = "Aged Receivable"
    _inherit = "account.aged.partner"

    @api.model
    def get_lines(self, context_id, line_id=None):
        if type(context_id) == int:
            context_id = self.env['account.context.aged.receivable'].search([['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_to': context_id.date_to,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'currency_ids': context_id.currency_ids.ids,
            'account_type': 'receivable',
        })
        return self.with_context(new_context)._lines(context_id, line_id)

    @api.model
    def get_title(self):
        context = self.env.context.get('context') or {}
        if context and context.get('aging_filter_cmp'):
            return _("Aged Receivable - Aging Report")
        if context and context.get('aging_due_filter_cmp'):
            return _("Aged Receivable - Due Aging Report")
        return _("Aged Receivable")

    @api.model
    def get_name(self):
        return 'aged_receivable'

    @api.model
    def get_report_type(self):
        return self.env.ref('enterprise_accounting_report.account_report_type_nothing')

    def get_template(self):
        return 'enterprise_accounting_report.report_financial'


class account_context_aged_receivable(models.TransientModel):
    _name = "account.context.aged.receivable"
    _description = "A particular context for the aged receivable"
    _inherit = "account.report.context.common"

    fold_field = 'unfolded_partners'
    unfolded_partners = fields.Many2many('res.partner', 'aged_receivable_context_to_partner', string='Unfolded lines')

    def get_report_obj(self):
        return self.env['account.aged.receivable']

    def get_columns_names(self):
        context = self.env.context
        # Aging filter (local currency)
        if context.get('aging_filter_cmp') and context.get('filter_local_currency'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("0&nbsp;-&nbsp;30"), _("31&nbsp;-&nbsp;60"),
                    _("61&nbsp;-&nbsp;90"), _("91&nbsp;-&nbsp;120"), _(">120"), _("Local&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age"), _("Currency"), _("Currency&nbsp;Rate")]
        # Aging filter (original currency)
        if context.get('aging_filter_cmp') and context.get('filter_original_currency'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("0&nbsp;-&nbsp;30"), _("31&nbsp;-&nbsp;60"),
                    _("61&nbsp;-&nbsp;90"), _("91&nbsp;-&nbsp;120"), _(">120"), _("Original&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age"), _("Currency"), _("Currency&nbsp;Rate")]
        # Due aging filter (local currency)
        if context.get('aging_due_filter_cmp') and context.get('filter_local_currency'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("Not&nbsp;Due"), _("0&nbsp;-&nbsp;30"),
                    _("31&nbsp;-&nbsp;60"), _("61&nbsp;-&nbsp;90"), _(">90"), _("Local&nbsp;Due"), _("Invoice&nbsp;Amount"),
                    _("Age"), _("Currency"), _("Currency&nbsp;Rate")]
        # Due aging filter (original currency)
        if context.get('aging_due_filter_cmp') and context.get('filter_original_currency'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("Not&nbsp;Due"), _("0&nbsp;-&nbsp;30"),
                    _("31&nbsp;-&nbsp;60"), _("61&nbsp;-&nbsp;90"), _(">90"), _("Original&nbsp;Due"), _("Invoice&nbsp;Amount"),
                    _("Age"), _("Currency"), _("Currency&nbsp;Rate")]
        # Aging filter only
        if context.get('aging_filter_cmp'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("Current"), _("1&nbsp;Mth"),
                    _("2&nbsp;Mth"), _("3&nbsp;Mth"), _(">3&nbsp;Mth"), _("Local&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age")]
        # Due aging filter only
        if context.get('aging_due_filter_cmp'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("Not&nbsp;Due"), _("1&nbsp;Mth"),
                    _("2&nbsp;Mth"), _("3&nbsp;Mth"), _(">3&nbsp;Mth"), _("Local&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age")]
        return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("0&nbsp;-&nbsp;30"), _("31&nbsp;-&nbsp;60"),
                _("61&nbsp;-&nbsp;90"), _("91&nbsp;-&nbsp;120"), _(">120"), _("Local&nbsp;Due"),
                _("Invoice&nbsp;Amount"), _("Age"), _("Currency"), _("Currency&nbsp;Rate")]

    @api.multi
    def get_columns_types(self):
        config_setting = self.env['account.config.settings'].search([],order='id desc', limit=1)
        if config_setting and config_setting.group_multi_currency:
            return ["number", "number", "number", "number", "number","number", "number", "number", "number", "number", "number", "number", "number"]
        else:
            return ["number", "number","number", "number", "number", "number", "number", "number", "number", "number", "number", "number", "number"]

class report_account_aged_payable(models.AbstractModel):
    _name = "account.aged.payable"
    _description = "Aged Payable"
    _inherit = "account.aged.partner"

    @api.model
    def get_lines(self, context_id, line_id=None):
        if type(context_id) == int:
            context_id = self.env['account.context.aged.payable'].search([['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_to': context_id.date_to,
            'aged_balance': True,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'currency_ids': context_id.currency_ids.ids,
            'account_type': 'payable',
        })
        return self.with_context(new_context)._lines(context_id, line_id)

    @api.model
    def get_title(self):
        context = self.env.context.get('context') or {}
        if context and context.get('aging_filter_cmp'):
            return _("Aged Payable - Aging Report")
        if context and context.get('aging_due_filter_cmp'):
            return _("Aged Payable - Due Aging Report")
        return _("Aged Payable")

    @api.model
    def get_name(self):
        return 'aged_payable'

    @api.model
    def get_report_type(self):
        return self.env.ref('enterprise_accounting_report.account_report_type_nothing')

    def get_template(self):
        return 'enterprise_accounting_report.report_financial'

class account_context_aged_payable(models.TransientModel):
    _name = "account.context.aged.payable"
    _description = "A particular context for the aged payable"
    _inherit = "account.report.context.common"

    fold_field = 'unfolded_partners'
    unfolded_partners = fields.Many2many('res.partner', 'aged_payable_context_to_partner', string='Unfolded lines')

    def get_report_obj(self):
        return self.env['account.aged.payable']

    def get_columns_names(self):
        context = self.env.context
        # Aging filter (local currency)
        if context.get('aging_filter_cmp') and context.get('filter_local_currency'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("0&nbsp;-&nbsp;30"), _("31&nbsp;-&nbsp;60"),
                    _("61&nbsp;-&nbsp;90"), _("91&nbsp;-&nbsp;120"), _(">120"), _("Local&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age"), _("Currency"), _("Currency&nbsp;Rate")]
        # Aging filter (original currency)
        if context.get('aging_filter_cmp') and context.get('filter_original_currency'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("0&nbsp;-&nbsp;30"), _("31&nbsp;-&nbsp;60"),
                    _("61&nbsp;-&nbsp;90"), _("91&nbsp;-&nbsp;120"), _(">120"), _("Original&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age"), _("Currency"), _("Currency&nbsp;Rate")]
        # Due aging filter (local currency)
        if context.get('aging_due_filter_cmp') and context.get('filter_local_currency'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("Not&nbsp;Due"), _("0&nbsp;-&nbsp;30"),
                    _("31&nbsp;-&nbsp;60"), _("61&nbsp;-&nbsp;90"), _(">90"), _("Local&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age"), _("Currency"), _("Currency&nbsp;Rate")]
        # Due aging filter (original currency)
        if context.get('aging_due_filter_cmp') and context.get('filter_original_currency'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("Not&nbsp;Due"), _("0&nbsp;-&nbsp;30"),
                    _("31&nbsp;-&nbsp;60"), _("61&nbsp;-&nbsp;90"), _(">90"), _("Original&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age"), _("Currency"), _("Currency&nbsp;Rate")]
        # Aging filter only
        if context.get('aging_filter_cmp'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("Current"), _("1&nbsp;Mth"),
                    _("2&nbsp;Mth"), _("3&nbsp;Mth"), _(">3&nbsp;Mth"), _("Local&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age")]
        # Due aging filter only
        if context.get('aging_due_filter_cmp'):
            return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("Not&nbsp;Due"), _("1&nbsp;Mth"),
                    _("2&nbsp;Mth"), _("3&nbsp;Mth"), _(">3&nbsp;Mth"), _("Local&nbsp;Due"),
                    _("Invoice&nbsp;Amount"), _("Age")]
        return [_("Invoice&nbsp;Date"), _("Due&nbsp;Date"), _("0&nbsp;-&nbsp;30"), _("31&nbsp;-&nbsp;60"),
                _("61&nbsp;-&nbsp;90"), _("91&nbsp;-&nbsp;120"), _(">120"), _("Local&nbsp;Due"),
                _("Invoice&nbsp;Amount"), _("Age"), _("Currency"), _("Currency&nbsp;Rate")]

    @api.multi
    def get_columns_types(self):
        config_setting = self.env['account.config.settings'].search([],order='id desc', limit=1)
        if config_setting and config_setting.group_multi_currency:
            return ["number", "number", "number", "number", "number","number", "number", "number", "number", "number", "number", "number", "number"]
        else:
            return ["number", "number","number", "number", "number","number", "number", "number", "number", "number", "number", "number", "number"]