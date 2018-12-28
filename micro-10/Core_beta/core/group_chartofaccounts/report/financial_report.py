import time
from datetime import datetime
from odoo import fields, models, api, _


class account_balance_inherit(models.AbstractModel):
    _inherit = "report.sg_account_report.financial_report_balance_full_temp"

    def _compute_account_balance(self, accounts):
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }
        res = {}
        for account in accounts:
            res[account.id] = dict((fn, 0.0) for fn in mapping.keys())
        if accounts:
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                      " FROM " + tables + \
                      " WHERE account_id IN %s " \
                      + filters + \
                      " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                # Balance computing based on percentage of ownership of company
                account = self.env['account.account'].browse(row['id'])
                company_ids = self.env['company.line'].search([('company_id', '=', account.company_id.id)])
                if company_ids and self.env.user.company_id.company_type == 'group_company' and self.env.user.company_id.company_line_ids:
                    row['debit'] = ((row['debit'] * company_ids.percentage) / 100)
                    row['credit'] = ((row['credit'] * company_ids.percentage) / 100)
                    row['balance'] = ((row['balance'] * company_ids.percentage) / 100)
                    res[row['id']] = row
                elif self.env.user.company_id.company_type == 'individual_company':
                    res[row['id']] = row
        return res

    def get_account_lines(self, data):
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        for report in child_reports:
            vals = {
                'name': report.name,
                'balance': res[report.id]['balance'] * report.sign,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type or False,  # used to underline the financial report balances
            }
            if data['columns'] == 'two':
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']
            if data['columns'] == 'four':
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']
                vals['ytd'] = res[report.id]['debit'] - res[report.id]['credit']
            if data['columns'] == 'five':
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']
                vals['ytd'] = res[report.id]['debit'] - res[report.id]['credit']
                vals['period'] = res[report.id]['debit'] - res[report.id]['credit']
            lines.append(vals)
            if report.display_detail == 'no_detail':
                continue
            if res[report.id].get('account'):
                sub_lines = []
                for account_id,values in res[report.id]['account'].items():
                    account = self.env['account.account'].browse(account_id)
                    flag = False
                    if account.company_type == 'group_company' and account.company_lines_ids:
                        main_bal = values['balance']
                        total_balance = 0.0
                        for account_line in account.company_lines_ids:
                            for acc,value in res[report.id]['account'].items():
                                if account_line.account_id.id == acc:
                                    total_balance += value['balance']
                        vals = {
                            'name': account.code + ' ' + account.name,
                            'balance': main_bal +total_balance * report.sign or 0.0,
                            'type': 'account',
                            'level': report.display_detail == 'detail_with_hierarchy' and 4,
                            'account_type': account.internal_type,
                        }
                        if data['columns'] == 'two':
                            vals['debit'] = values['debit']
                            vals['credit'] = values['credit']
                            if not account.company_id.currency_id.is_zero(
                                    vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                                flag = True
                        if data['columns'] == 'four':
                            vals['debit'] = values['debit']
                            vals['credit'] = values['credit']
                            vals['ytd'] = values['debit'] - values['credit']
                            if not account.company_id.currency_id.is_zero(
                                    vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                                flag = True
                        if data['columns'] == 'five':
                            vals['debit'] = values['debit']
                            vals['credit'] = values['credit']
                            vals['ytd'] = values['debit'] - values['credit']
                            vals['period'] = values['debit'] - values['credit']
                            if not account.company_id.currency_id.is_zero(
                                    vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                                flag = True
                        if not account.company_id.currency_id.is_zero(vals['balance']):
                            flag = True
                    elif self.env.user.company_id.company_type == 'individual_company':
                        vals = {
                            'name': account.code + ' ' + account.name,
                            'balance': values['balance'] * report.sign or 0.0,
                            'type': 'account',
                            'level': report.display_detail == 'detail_with_hierarchy' and 4,
                            'account_type': account.internal_type,
                        }
                        if data['columns'] == 'two':
                            vals['debit'] = values['debit']
                            vals['credit'] = values['credit']
                            if not account.company_id.currency_id.is_zero(
                                    vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                                flag = True
                        if data['columns'] == 'four':
                            vals['debit'] = values['debit']
                            vals['credit'] = values['credit']
                            vals['ytd'] = values['debit'] - values['credit']
                            if not account.company_id.currency_id.is_zero(
                                    vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                                flag = True
                        if data['columns'] == 'five':
                            vals['debit'] = values['debit']
                            vals['credit'] = values['credit']
                            vals['ytd'] = values['debit'] - values['credit']
                            vals['period'] = values['debit'] - values['credit']
                            if not account.company_id.currency_id.is_zero(
                                    vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
                                flag = True
                        if not account.company_id.currency_id.is_zero(vals['balance']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])

        return lines

    @api.multi
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        docargs = {'doc_ids': self.ids,
                   'doc_model': self.model,
                   'data': data,
                   'docs': docs,
                   'time': time,
                   'get_account_lines': self.get_account_lines(data.get('form')),
                   }
        return self.env['report'].render('sg_account_report.financial_report_balance_full_temp', docargs)


################################################################
class account_balance_inherit_qtr(models.AbstractModel):
    _inherit = "report.sg_account_report.account_full_qtr_balance_cols"

    def _compute_account_balance(self, accounts):
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }
        res = {}
        for account in accounts:
            res[account.id] = dict((fn, 0.0) for fn in mapping.keys())
        if accounts:
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                      " FROM " + tables + \
                      " WHERE account_id IN %s " \
                      + filters + \
                      " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                # Balance computing based on percentage of ownership of company
                account = self.env['account.account'].browse(row['id'])
                company_ids = self.env['company.line'].search([('company_id', '=', account.company_id.id)])
                if company_ids and self.env.user.company_id.company_type == 'group_company' and self.env.user.company_id.company_line_ids:
                    row['debit'] = ((row['debit'] * company_ids.percentage) / 100)
                    row['credit'] = ((row['credit'] * company_ids.percentage) / 100)
                    row['balance'] = ((row['balance'] * company_ids.percentage) / 100)
                    res[row['id']] = row
                elif self.env.user.company_id.company_type == 'individual_company':
                    res[row['id']] = row
        return res

    def get_account_lines_qtr(self, data):
        res = {}
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        acc_bal_obj = self.env['report.sg_account_report.financial_report_balance_full_temp']
        child_reports = account_report._get_children_by_order()
        if data['qtr_dates'] and data['quat_num']:
            for qtr in range(data['quat_num']):
                data['used_context']['date_from'] = data['qtr_dates']['qtr' + str(qtr + 1)]['date_from']
                data['used_context']['date_to'] = data['qtr_dates']['qtr' + str(qtr + 1)]['date_to']
                res1 = acc_bal_obj.with_context(data.get('used_context'))._compute_report_balance(child_reports)
                res.update({'qtn' + str(qtr + 1): res1})
                res1 = {}
        for report in child_reports:
            vals = {
                'name': report.name,
                'balance1': res['qtn1'][report.id]['balance'] * report.sign or 0.0,
                'balance2': 0.0,
                'balance3': 0.0,
                'balance4': 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'ytd': (res['qtn1'][report.id]['debit'] - res['qtn1'][report.id]['credit']) or 0.0,
                'account_type': report.type or False,  # used to underline the financial report balances
            }
            if data['quat_num'] == 2:
                vals.update({
                    'balance2': res['qtn2'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 3:
                vals.update({
                    'balance3': res['qtn3'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 4:
                vals.update({
                    'balance4': res['qtn4'][report.id]['balance'] * report.sign or 0.0,
                })
            lines.append(vals)
            if report.display_detail == 'no_detail':
                continue
            if res['qtn1'][report.id].get('account'):
                for account_id, values in res['qtn1'][report.id]['account'].items():
                    account = self.env['account.account'].browse(account_id)
                    flag = False
                    if account.company_type == 'group_company' and account.company_lines_ids:
                        main_bal = values['balance']
                        total_balance = 0.0
                        for account_line in account.company_lines_ids:
                            for acc, value in res['qtn1'][report.id]['account'].items():
                                if account_line.account_id.id == acc:
                                    total_balance += value['balance']
                        vals = {
                            'name': account.code + ' ' + account.name,
                            'balance1': main_bal +total_balance * report.sign or 0.0,
                            'balance2': 0.0,
                            'balance3': 0.0,
                            'balance4': 0.0,
                            'type': 'account',
                            'level': report.display_detail == 'detail_with_hierarchy' and 4,
                            'ytd': (values['debit'] - values['credit']) or 0.0,
                            'account_type': account.internal_type,
                        }
                        if data['quat_num'] == 2:
                            if account_id in res['qtn2'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance2': res['qtn2'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 3:
                            if account_id in res['qtn3'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance3': res['qtn3'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 4:
                            if account_id in res['qtn4'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance4': res['qtn4'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                    elif self.env.user.company_id.company_type == 'individual_company':
                        vals = {
                            'name': account.code + ' ' + account.name,
                            'balance1': values['balance'] * report.sign or 0.0,
                            'balance2': 0.0,
                            'balance3': 0.0,
                            'balance4': 0.0,
                            'type': 'account',
                            'level': report.display_detail == 'detail_with_hierarchy' and 4,
                            'ytd': (values['debit'] - values['credit']) or 0.0,
                            'account_type': account.internal_type,
                        }
                        if data['quat_num'] == 2:
                            if account_id in res['qtn2'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance2': res['qtn2'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 3:
                            if account_id in res['qtn3'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance3': res['qtn3'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 4:
                            if account_id in res['qtn4'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance4': res['qtn4'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                lines.append(vals)
        return lines

    @api.multi
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        docargs = {'doc_ids': self.ids,
                   'doc_model': self.model,
                   'data': data,
                   'docs': docs,
                   'time': time,
                   'get_account_lines_qtr': self.get_account_lines_qtr(data.get('form')),
                   }
        return self.env['report'].render('sg_account_report.account_full_qtr_balance_cols', docargs)


class account_balance_inherit_twlv(models.AbstractModel):
    _inherit = "report.sg_account_report.account_full_13_balance_cols"

    def _compute_account_balance(self, accounts):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            company_ids = self.env['company.line'].search([('company_id', '=', account.company_id.id)])
            if company_ids and self.env.user.company_id.company_type == 'group_company' and self.env.user.company_id.company_line_ids:
                res[account.id] = dict((fn, 0.0) for fn in mapping.keys())
        if accounts:
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                #Balance computing based on percentage of ownership of company
                account = self.env['account.account'].browse(row['id'])
                company_ids = self.env['company.line'].search([('company_id', '=', account.company_id.id)])
                if company_ids and self.env.user.company_id.company_type == 'group_company' and self.env.user.company_id.company_line_ids:
                    row['debit'] = ((row['debit'] * company_ids.percentage) / 100)
                    row['credit'] = ((row['credit'] * company_ids.percentage) / 100)
                    row['balance'] = ((row['balance'] * company_ids.percentage) / 100)
                    res[row['id']] = row
                elif self.env.user.company_id.company_type == 'individual_company':
                    res[row['id']] = row

        return res

    def get_account_lines_twelve_month(self, data):
        lines = []
        account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
        acc_bal_obj = self.env['report.sg_account_report.financial_report_balance_full_temp']
        child_reports = account_report._get_children_by_order()
        res = {}

        if data['qtr_dates'] and data['quat_num']:
            for qtr in range(data['quat_num']):
                data['used_context']['date_from'] = data['qtr_dates']['qtr' + str(qtr + 1)]['date_from']
                data['used_context']['date_to'] = data['qtr_dates']['qtr' + str(qtr + 1)]['date_to']
                res1 = acc_bal_obj.with_context(data.get('used_context'))._compute_report_balance(child_reports)
                res.update({'qtn' + str(qtr + 1): res1})
        for report in child_reports:
            vals = {
                'name': report.name,
                'balance1': res['qtn1'][report.id]['balance'] * report.sign or 0.0,
                'balance2': 0.0,
                'balance3': 0.0,
                'balance4': 0.0,
                'balance5': 0.0,
                'balance6': 0.0,
                'balance7': 0.0,
                'balance8': 0.0,
                'balance9': 0.0,
                'balance10': 0.0,
                'balance11': 0.0,
                'balance12': 0.0,
                'ytd': (res['qtn1'][report.id]['debit'] - res['qtn1'][report.id]['credit']) or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type or False,  # used to underline the financial report balances
            }
            if data['quat_num'] == 2:
                vals.update({
                    'balance2': res['qtn2'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 3:
                vals.update({
                    'balance3': res['qtn3'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 4:
                vals.update({
                    'balance4': res['qtn4'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 5:
                vals.update({
                    'balance5': res['qtn5'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 6:
                vals.update({
                    'balance6': res['qtn6'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 7:
                vals.update({
                    'balance7': res['qtn7'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 8:
                vals.update({
                    'balance8': res['qtn8'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 9:
                vals.update({
                    'balance9': res['qtn9'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 10:
                vals.update({
                    'balance10': res['qtn10'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 11:
                vals.update({
                    'balance11': res['qtn11'][report.id]['balance'] * report.sign or 0.0,
                })
            if data['quat_num'] == 12:
                vals.update({
                    'balance12': res['qtn12'][report.id]['balance'] * report.sign or 0.0,
                })

            lines.append(vals)
            if report.display_detail == 'no_detail':
                # the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue

            if res['qtn1'][report.id].get('account'):
                for account_id, values in res['qtn1'][report.id]['account'].items():
                    account = self.env['account.account'].browse(account_id)
                    flag = False
                    if account.company_type == 'group_company' and account.company_lines_ids:
                        main_bal = values['balance']
                        total_balance = 0.0
                        for account_line in account.company_lines_ids:
                            for acc, value in res['qtn1'][report.id]['account'].items():
                                if account_line.account_id.id == acc:
                                    total_balance += value['balance']
                        vals = {
                            'name': account.code + ' ' + account.name,
                            'balance1': main_bal + total_balance * report.sign or 0.0,
                            'balance2': 0.0,
                            'balance3': 0.0,
                            'balance4': 0.0,
                            'balance5': 0.0,
                            'balance6': 0.0,
                            'balance7': 0.0,
                            'balance8': 0.0,
                            'balance9': 0.0,
                            'balance10': 0.0,
                            'balance11': 0.0,
                            'balance12': 0.0,
                            'type': 'account',
                            'ytd': (values['debit'] - values['credit']) or 0.0,
                            'level': report.display_detail == 'detail_with_hierarchy' and 4,
                            'account_type': account.internal_type,
                        }
                        if data['quat_num'] == 2:
                            if account_id in res['qtn2'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance2': res['qtn2'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 3:
                            if account_id in res['qtn3'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance3': res['qtn3'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 4:
                            if account_id in res['qtn4'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance4': res['qtn4'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 5:
                            if account_id in res['qtn5'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance5': res['qtn5'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 6:
                            if account_id in res['qtn6'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance6': res['qtn6'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 7:
                            if account_id in res['qtn7'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance7': res['qtn7'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 8:
                            if account_id in res['qtn8'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance8': res['qtn8'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 9:
                            if account_id in res['qtn9'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance9': res['qtn9'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 10:
                            if account_id in res['qtn10'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance10': res['qtn10'][report.id]['account'][account_id][
                                                     'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 11:
                            if account_id in res['qtn11'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance11': res['qtn11'][report.id]['account'][account_id][
                                                     'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 12:
                            if account_id in res['qtn12'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance12': res['qtn12'][report.id]['account'][account_id][
                                                     'balance'] * report.sign or 0.0,
                                })
                    elif self.env.user.company_id.company_type == 'individual_company':
                        vals = {
                            'name': account.code + ' ' + account.name,
                            'balance1': values['balance'] * report.sign or 0.0,
                            'balance2': 0.0,
                            'balance3': 0.0,
                            'balance4': 0.0,
                            'balance5': 0.0,
                            'balance6': 0.0,
                            'balance7': 0.0,
                            'balance8': 0.0,
                            'balance9': 0.0,
                            'balance10': 0.0,
                            'balance11': 0.0,
                            'balance12': 0.0,
                            'type': 'account',
                            'ytd': (values['debit'] - values['credit']) or 0.0,
                            'level': report.display_detail == 'detail_with_hierarchy' and 4,
                            'account_type': account.internal_type,
                        }
                        if data['quat_num'] == 2:
                            if account_id in res['qtn2'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance2': res['qtn2'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 3:
                            if account_id in res['qtn3'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance3': res['qtn3'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 4:
                            if account_id in res['qtn4'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance4': res['qtn4'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 5:
                            if account_id in res['qtn5'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance5': res['qtn5'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 6:
                            if account_id in res['qtn6'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance6': res['qtn6'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 7:
                            if account_id in res['qtn7'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance7': res['qtn7'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 8:
                            if account_id in res['qtn8'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance8': res['qtn8'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 9:
                            if account_id in res['qtn9'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance9': res['qtn9'][report.id]['account'][account_id][
                                                    'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 10:
                            if account_id in res['qtn10'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance10': res['qtn10'][report.id]['account'][account_id][
                                                     'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 11:
                            if account_id in res['qtn11'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance11': res['qtn11'][report.id]['account'][account_id][
                                                     'balance'] * report.sign or 0.0,
                                })
                        if data['quat_num'] == 12:
                            if account_id in res['qtn12'][report.id]['account']:
                                flag = False
                                vals.update({
                                    'balance12': res['qtn12'][report.id]['account'][account_id][
                                                     'balance'] * report.sign or 0.0,
                                })
                lines.append(vals)
        return lines

    @api.multi
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        docargs = {'doc_ids': self.ids,
                   'doc_model': self.model,
                   'data': data,
                   'docs': docs,
                   'time': time,
                   'get_account_lines_twelve_month': self.get_account_lines_twelve_month(data.get('form')),
                   }
        return self.env['report'].render('sg_account_report.account_full_13_balance_cols', docargs)