# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import UserError
import collections
from datetime import datetime
from odoo.tools import float_is_zero
from dateutil.relativedelta import relativedelta
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class ReportAccounTtransaction(models.AbstractModel):
    _name = 'report.account.report_agedpartnerbalance'

    def _get_partner_move_lines(self, account_type, date_from, target_move, period_length):
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
                AND (l.date <= %s)
                AND l.company_id = %s
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        partner_ids = self.env['res.partner'].search([('id','in',partner_ids),('user_ids','=',self.env.user.id)]).ids
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], []

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) > %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id = %s'''
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
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
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

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id = %s'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                if not line.invoice_id:
                    continue
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
                        'period': i + 1,
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

    @api.model
    def _get_invoices(self, partner_ids, date_from, date_to, type, period_length, target_move,account_type):
        periods = {}
        data = {}
        start = date_from
        stop = False
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            periods[i] = {
                'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                'stop': start.strftime(DF),
                'start': (i!=0 and stop.strftime(DF) or False),
            }
            start = stop - relativedelta(days=1)
        dates_query = '(COALESCE(l.date_maturity,l.date) BETWEEN %s AND %s) '
        cr = self.env.cr
        user_company = self.env.user.company_id.id
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']

        arg_list = (tuple(move_state), tuple(account_type))
        if not partner_ids:
            return data, periods
        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (l.partner_id IN %s)
                AND (l.date <= %s)
                AND (l.company_id = %s)
                AND (l.reconciled IS FALSE)
                OR (COALESCE(l.date_maturity,l.date) > %s)
                AND '''+dates_query


        cr.execute(query, (tuple(move_state), tuple(account_type), tuple(partner_ids), date_from,  user_company,date_from, stop, date_from))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        group_by_inv = {}
        move_line_list = []
        for line in self.env['account.move.line'].browse(aml_ids):
            if line.invoice_id:
                move_line_list.append(line)
        for line in move_line_list:
            group_by_inv.setdefault(line.invoice_id.id, [])
            group_by_inv[line.invoice_id.id].append(line)
        group_by_inv = collections.OrderedDict(sorted(group_by_inv.items()))
        data_inv = {}
        for inv, lines in group_by_inv.items():
#             inv = self.env['account.invoice'].browse(inv)
            for line in lines:
                data_inv.setdefault(inv, [0,0,0,0,0,0])
                for i in range(5):
                    date_maturity = datetime.strptime(line.date_maturity, DF)
                    if (not periods[i]['start'] or date_maturity>=datetime.strptime(periods[i]['start'], DF)) and date_maturity<=datetime.strptime(periods[i]['stop'], DF):
                        data_inv[inv][i] += line.amount_residual
        date_from = str(date_from)
        date_from = date_from.split(' ')
        user_partner_ids = self.env['res.partner'].search(['|', ('user_ids','=',self.env.user.id),('user_ids','=',False)]).ids
        for invoice, periods_amt in data_inv.items():
            invoice = self.env['account.invoice'].browse(invoice)
            due_date = invoice.date_due
            if not due_date:
                due_date = invoice.date_invoice 
            total_date = datetime.strptime(str(date_from[0]), DF) - datetime.strptime(str(due_date), DF)
            total_days = total_date.days
            not_due = 0.0
            if total_days < 0 :
                not_due = invoice.amount_total_company_signed
                if invoice.type != 'out_invoice' or invoice.type != 'out_refund':
                    not_due = -not_due
            if invoice and (invoice.partner_id.id in user_partner_ids):
                data.setdefault((invoice.id), [])
                data[(invoice.id)].append({
                'partner':invoice.partner_id.name,                                                          
                'currency_id':invoice.currency_id,
                'amount':invoice.amount_total,
                'amount_company':invoice.amount_total_company_signed,
                'date':invoice.date_invoice and datetime.strptime(invoice.date_invoice, DF).strftime('%d/%m/%Y') or '',
                'company_currency': invoice.company_id.currency_id,
                'number':invoice.number,
                'rate': round(invoice.amount_total_company_signed/invoice.amount_total,2),
                'periods':periods_amt,
                'not_due':not_due
                })
        return data, periods

    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['form'].get('date_from') and datetime.strptime(data['form']['date_from'], DF) or False
        
        date_to = data['form'].get('date_to', False) and datetime.strptime(data['form']['date_to'], DF) or False

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']

        target_move = data['form'].get('target_move', 'all')
#         partner_ids = data['form']['partner_ids']
#         if not partner_ids:
        dom = []
        if data['form']['result_selection'] == 'customer':
            dom.append(('customer', '=', True))
        if data['form']['result_selection'] == 'supplier':
            dom.append(('supplier', '=', True))
        data['form']['company_currency'] = docs.company_id.currency_id.name
        partner_ids = self.env['res.partner'].search(dom).ids
        invoices, periods = self._get_invoices(partner_ids, date_from, date_to,data['form']['result_selection'], data['form']['period_length'], target_move, account_type)
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))

        currency={}
        balance_id = data['context']['active_id']
        balance_id = self.env['account.aged.trial.balance'].browse(balance_id)
        foreign_currency = balance_id.foreign_currency
        if foreign_currency == True:
            currency['foreign_currency'] = 1
        else:
            currency['foreign_currency'] = 0

        movelines, total, dummy = self._get_partner_move_lines(account_type, date_from, target_move, data['form']['period_length'])
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'type': data['form']['result_selection'],
            'invoices':invoices,
            'periods': periods,
            'currency':currency,
            'time': time,
            'get_partner_lines': movelines,
            'get_direction': total,
        }
        if balance_id.export_format == 'summary':
            return self.env['report'].render('account.report_agedpartnerbalance', docargs)
        else:
            return self.env['report'].render('aged_partner_balances.report_agedpartnerbalance2', docargs)