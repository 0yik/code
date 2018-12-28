# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

import base64
import StringIO
import xlsxwriter
import csv
import os.path


class AccountTransactionReport(models.TransientModel):

    _name = 'account.aged.forex.report'
    _inherit = 'account.common.partner.report'
    _description = 'Account Foreign Currency Report'

    @api.onchange('result_selection')
    def onchange_result_selection(self):
        if self.result_selection=='customer':
            return {'domain': {'partner_ids' : [('customer', '=', True)]}}
        elif self.result_selection=='supplier':
            return {'domain': {'partner_ids' : [('supplier', '=', True)]}}
        else:
            return {'domain': {'partner_ids' : ['|', ('customer', '=', True), ('supplier', '=', True)]}}

    @api.model
    def _get_invoices(self, partner_ids, date_from, date_to, type, period_length, target_move,account_type):
        periods = {}
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

        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (l.partner_id IN %s)
                AND (l.date <= %s)
                AND (l.company_id = %s)
                AND (l.reconciled IS FALSE)
                AND '''+dates_query


        cr.execute(query, (tuple(move_state), tuple(account_type), tuple(partner_ids), date_from,  user_company, stop, date_from))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        data = {}
        group_by_inv = {}
        for line in self.env['account.move.line'].browse(aml_ids):
            group_by_inv.setdefault(line.invoice_id, [])
            group_by_inv[line.invoice_id].append(line)
        data_inv = {}
        for inv, lines in group_by_inv.items():
            for line in lines:
                data_inv.setdefault(inv, [0,0,0,0,0,0])
                for i in range(5):
                    date_maturity = datetime.strptime(line.date_maturity, DF)
                    if (not periods[i]['start'] or date_maturity>=datetime.strptime(periods[i]['start'], DF)) and date_maturity<=datetime.strptime(periods[i]['stop'], DF):
                        data_inv[inv][i] += line.amount_residual
        for invoice, periods_amt in data_inv.items():
            if invoice:
                data.setdefault((invoice.partner_id.id, invoice.partner_id.name), [])
                data[(invoice.partner_id.id, invoice.partner_id.name)].append({
                'currency_id':invoice.currency_id,
                'amount':invoice.amount_total,
                'amount_company':invoice.amount_total_company_signed,
                'date':invoice.date_invoice and datetime.strptime(invoice.date_invoice, DF).strftime('%d/%m/%Y') or '',
                'company_currency': invoice.company_id.currency_id,
                'number':invoice.number,
                'rate': round(invoice.amount_total_company_signed/invoice.amount_total,2),
                'periods':periods_amt,
                })

        return data, periods


    partner_ids = fields.Many2many('res.partner', string='Partners')
    period_length = fields.Integer(string='Period Length (days)', required=True, default=30)

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'partner_ids': self.read(['partner_ids'])[0]['partner_ids'], 
            'company_currency': self.env.user.company_id.currency_id.name,
            'period_length': self.read(['period_length'])[0]['period_length']})
        return self.env['report'].with_context(landscape=True).get_action(self, 'sg_ageingreport_forex.report_agedforeigncurrency', data=data)

    def export_excel(self):
        data = self.check_report()
        data = self.pre_print_report(data['data'])
        date_from = data['form'].get('date_from') and datetime.strptime(data['form']['date_from'], DF) or False
        
        date_to = data['form'].get('date_to', False) and datetime.strptime(data['form']['date_to'], DF) or False
        
        account_type_display = ''
        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
            account_type_display = 'Receivable Accounts'
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
            account_type_display = 'Payable Accounts'
        else:
            account_type = ['payable', 'receivable']
            account_type_display = 'Receivable & Payable Accounts'

        target_move = data['form'].get('target_move', 'all')
        if target_move=='all':
            target_move_display = 'All Entries'
        else:
            target_move_display = 'All Posted Entries'
        partner_ids = data['form']['partner_ids']
        if not partner_ids:
            dom = []
            if data['form']['result_selection'] == 'customer':
                dom.append(('customer', '=', True))
            if data['form']['result_selection'] == 'supplier':
                dom.append(('supplier', '=', True))

            partner_ids = self.env['res.partner'].search(dom).ids
        invoices, periods = self._get_invoices(partner_ids, date_from, date_to,data['form']['result_selection'], data['form']['period_length'], target_move, account_type)
        date_from_move = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        output =  StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sheet1')
        row = 0
        col = 0
        bold_format = workbook.add_format({'bold':  1})
        right_format = workbook.add_format({'bold':1,'align':'right'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter'})
        font_size_format = workbook.add_format()
        font_size_format.set_font_size(10.5)

        if date_from:
            worksheet.write(row, col,  unicode('Start Date', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col,  data['form']['date_from'],font_size_format)
            worksheet.set_column(row, col, 20)
            col += 2

        worksheet.write(row, col,  unicode('Period Length', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col,  data['form']['period_length'],font_size_format)
        worksheet.set_column(row, col, 20)
        row += 1
        col = 0
        worksheet.write(row, col,  unicode('Partner"s', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col,  account_type_display,font_size_format)
        worksheet.set_column(row, col, 20)
        col +=2

        worksheet.write(row, col,  unicode('Target Move', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col,  target_move_display,font_size_format)
        worksheet.set_column(row, col, 20)

        col = 0
        row += 1
        
        worksheet.write(row, col,  unicode('Name', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Date', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Invoice reference', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Amount (foreign Currency)', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Currency', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Exchange rate on the date', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Amount in SGD', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        # col = 0
        col += 1
        keys = periods.keys()
        keys.reverse()
        for period in keys:
            worksheet.write(row, col, periods[period]['name'], bold_format)
            worksheet.set_column(row, col, 20)
            col += 1
        for inv_key,inv_details in invoices.items(): 
            col = 0
            row += 1
            worksheet.write(row, col, inv_key[1], bold_format)
            worksheet.set_column(row, col, 20)
            col = 0
            row += 1
            for inv in inv_details:
                col = 0
                worksheet.write(row, col, '', font_size_format)
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['date'], font_size_format)
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['number'], font_size_format)
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['amount'], font_size_format)
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['currency_id'].name, font_size_format)
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['rate'], font_size_format)
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['amount_company'], font_size_format)
                worksheet.set_column(row, col, 20)
                col += 1
                for i in [4,3,2,1,0,]:
                    worksheet.write(row, col, inv['periods'][i], font_size_format)
                    worksheet.set_column(row, col, 20)
                    col += 1 

        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({'name': 'AgedForeignCurrency.xls', 'datas_fname': 'AgedForeignCurrency.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
                "target": "self",
            }