# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from datetime import date, datetime, timedelta
from odoo.tools.translate import _
from odoo import api, models

from odoo.tools import float_is_zero
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pprint

# Mixin to use with rml_parse, so self.pool will be defined.
class common_report_header(object):    
    #FOR DAILY REPORT
    def _get_account_daily_report(self, account_daily):
        cr = self.cr
        uid = self.uid
        daily_ids = []
        daily_cash_obj = self.env['daily.report.cashbank']
        for daily_cash in daily_cash_obj.browse(account_daily):
            res_cash = {}
            res_cash['account_id'] = daily_cash.account_id.id
            res_cash['amount'] = daily_cash.amount
            res_cash['notes'] = daily_cash.notes
            daily_ids.append(daily_cash.account_id.id)
        return daily_ids
    
    def _get_account_move_init_balance(self, data, accounts, init_balance, sortby, display_account):
        #print """ _get_account_move_init_balance """,data['date'],account_type
        cr = self.cr
        uid = self.uid
        date_from = False#time.strftime('%Y-%m-01', time.strptime(data['date'],'%Y-%m-%d'))
        date_first_to = time.strftime('%Y-%m-01', time.strptime(data['date'],'%Y-%m-%d'))
        date_to = datetime.strptime(date_first_to, DEFAULT_SERVER_DATE_FORMAT).date() - timedelta(days=1)        
        MoveLine = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))
        #print "===init_balance==",date_from,date_to
        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=date_from, date_to=date_to)._query_get_daily()#MoveLine.with_context(date_to=self.context.get('date_from'), date_from=False)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, 'Starting Balance' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                NULL AS currency_id,\
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                '' AS partner_name\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                JOIN account_journal j ON (l.journal_id=j.id)\
                WHERE l.account_id IN %s" + filters + ' GROUP BY l.account_id')
            #print "==sql==",accounts.ids,init_where_params
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)
                #print "====row====",row
        #print "===move_lines===",move_lines
        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'
        #dailyc_ids = []
        daily_ids = dict(map(lambda x: (x, []), accounts.ids))
        for dailyc in self.env['daily.report.cashbank'].browse(data['daily_cashbank_ids']):
            daily_ids[dailyc.account_id.id].append(dailyc)
        # Calculate the debit, credit and balance for Accounts
        account_res = []
        #print "===accounts===",accounts
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['id'] = account.id
            res['code'] = account.code
            res['name'] = account.name
            res['sfr'] = daily_ids[res['id']][0].amount
            res['as'] = daily_ids[res['id']][0].notes
            res['sr'] = 0.0
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
        #print "====account_res====",account_res
        return account_res
    
    def _get_account_move_counter_part(self, data, account, account_sum):
        #print "===_get_account_move_counter_part===",account
        cr = self.cr
        MoveLine = self.env['account.move.line']
        date_from = time.strftime('%Y-%m-01', time.strptime(data['date'],'%Y-%m-%d'))
        date_to = time.strftime('%Y-%m-%d', time.strptime(data['date'],'%Y-%m-%d'))
        #move_lines = dict(map(lambda x: (x, []), accounts.ids))
        #move_line_ids = MoveLine.search(self.cr, self.uid, [('move_id','=',l['mmove_id']),('account_id','!=',account.id)])
        sql_sort = 'l.date, l.move_id'
        #print "====get_lines===",date_from,date_to
#         if sortby == 'sort_journal_partner':
#             sql_sort = 'j.code, p.name, l.move_id'
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine.with_context(date_to=date_to, date_from=date_from)._query_get_daily()
        #print '===tables, where_clause, where_params==',where_params
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, m.id AS mmove_id, c.symbol AS currency_code, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id = '+ str(account) +' ' + filters + ' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, m.id, c.symbol, p.name ORDER BY ' + sql_sort)
        params = tuple(where_params)
        cr.execute(sql, params)
        lines = []
        for line_row in cr.dictfetchall():
            move_line_ids = MoveLine.search([('move_id','=',line_row['mmove_id']),('account_id','!=',account)])
            #print "===move_line_ids==",move_line_ids
            line_row['laccid'] = ''
            line_row['lacc'] = ''
            line_row['lidd'] = ''
            for line_move in move_line_ids:
                line_row['lacc'] = line_move.account_id.name
                line_row['lidd'] = line_move.id
                line_row['laccid'] = line_move.account_id.id
                lines.append(line_move.id)
        #print "====lines==",lines
        res = {}
        if lines != []:
            if len(lines) == 1:
                if data['display_type'] == 'summary':# or data['display_type_bank'] == 'summary':
                    sql_counter = ('SELECT 0 AS lid, l.account_id AS account_id, acc.name AS lref, acc.code AS lname, COALESCE(SUM(l.debit),0.0) AS credit, COALESCE(SUM(l.credit),0.0) AS debit \
                        FROM account_move_line l\
                        JOIN account_move m ON (l.move_id=m.id)\
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                        JOIN account_journal j ON (l.journal_id=j.id)\
                        JOIN account_account acc ON (l.account_id = acc.id) \
                        WHERE l.id = '+ str(lines[0]) +' ' + filters + ' GROUP BY l.account_id,acc.name,acc.code')
                #print "====line1====summary",sql_counter,lines
                if data['display_type'] == 'detail':
                    sql_counter = ('SELECT 0 AS lid, l.account_id AS account_id, acc.name AS lref, l.name AS lname, m.name AS move_name, l.date AS ldate, COALESCE(SUM(l.debit),0.0) AS credit, COALESCE(SUM(l.credit),0.0) AS debit \
                        FROM account_move_line l\
                        JOIN account_move m ON (l.move_id=m.id)\
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                        JOIN account_journal j ON (l.journal_id=j.id)\
                        JOIN account_account acc ON (l.account_id = acc.id) \
                        WHERE l.id = '+ str(lines[0]) +' ' + filters + ' GROUP BY l.id,acc.name,l.name,m.name ORDER BY l.date')
                    #print "====line1====detail",sql_counter,lines
                cr.execute(sql_counter, tuple(where_params))
            else:
                if data['display_type'] == 'summary':
                    sql_counter = ('SELECT 0 AS lid, l.account_id AS account_id, acc.name AS lref, acc.code AS lname, COALESCE(SUM(l.debit),0.0) AS credit, COALESCE(SUM(l.credit),0.0) AS debit \
                        FROM account_move_line l\
                        JOIN account_move m ON (l.move_id=m.id)\
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                        JOIN account_journal j ON (l.journal_id=j.id)\
                        JOIN account_account acc ON (l.account_id = acc.id) \
                        WHERE l.id IN %s ' + filters + ' GROUP BY l.account_id,acc.name,acc.code')
                if data['display_type'] == 'detail':
                    sql_counter = ('SELECT 0 AS lid, l.account_id AS account_id, acc.name AS lref, l.name AS lname, m.name AS move_name, l.date AS ldate, COALESCE(SUM(l.debit),0.0) AS credit, COALESCE(SUM(l.credit),0.0) AS debit \
                        FROM account_move_line l\
                        JOIN account_move m ON (l.move_id=m.id)\
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                        JOIN account_journal j ON (l.journal_id=j.id)\
                        JOIN account_account acc ON (l.account_id = acc.id) \
                        WHERE l.id IN %s ' + filters + ' GROUP BY l.id,acc.name,l.name,m.name ORDER BY l.date')
                    #print "====line>1====detail",sql_counter,lines
                cr.execute(sql_counter, (tuple(lines),) + tuple(where_params))
            #account_sum = 0.0
            #print "===sql_counter===",sql_counter,lines
            res_counter = cr.dictfetchall()
            res = res_counter
            for line_cou in res:
                line_cou['lacc'] = ''
                account_sum += line_cou['debit'] - line_cou['credit']
                #line_cou['date'] = line_cou['date']
                line_cou['lname'] = line_cou['lname']
                if data['display_type'] == 'detail':
                    line_cou['ldate'] = line_cou['ldate']
                    line_cou['move_name'] = line_cou['move_name']
                line_cou['progress'] = account_sum
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
