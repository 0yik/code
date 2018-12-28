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

    _name = 'account.transaction.report'
    _inherit = 'account.common.partner.report'
    _description = 'Account Receivable Transaction Report'

    @api.onchange('result_selection')
    def onchange_result_selection(self):
        if self.result_selection=='customer':
            return {'domain': {'partner_ids' : [('customer', '=', True)]}}
        elif self.result_selection=='supplier':
            return {'domain': {'partner_ids' : [('supplier', '=', True)]}}
        else:
            return {'domain': {'partner_ids' : ['|', ('customer', '=', True), ('supplier', '=', True)]}}

    partner_ids = fields.Many2many('res.partner', string='Partners')
    invoice_state = fields.Selection([('not_paid', 'Not Paid'), ('paid', 'Paid'), ('all', 'All')], default='not_paid')

    @api.model
    def _get_invoices(self, partner_ids, date_from, date_to, state, type):
        dom = []
        if date_from:
            dom.append(['date_invoice', '>=', date_from])
        if date_to:
            dom.append(['date_invoice', '<=', date_to])
        if state=='not_paid':
            dom.append(['state', 'not in', ['draft', 'paid']])
        elif state=='paid':
            dom.append(['state', '=', 'paid'])
        if partner_ids:
            dom.append(('partner_id', 'in', partner_ids))
        if type=='customer':
            dom.append(('type', '=', 'out_invoice'))
        elif type=='supplier':
            dom.append(('type', '=', 'in_invoice'))
        invoices = self.env['account.invoice'].search(dom)
        data = {}
        for invoice in invoices:
            data.setdefault((invoice.partner_id.id, invoice.partner_id.name), [])
            data[(invoice.partner_id.id, invoice.partner_id.name)].append({
                'currency_id':invoice.currency_id,
                'amount':invoice.amount_total,
                'amount_company':invoice.amount_total_company_signed,
                'date':invoice.date_invoice and datetime.strptime(invoice.date_invoice, DF).strftime('%d/%m/%Y') or '',
                'company_currency': invoice.company_id.currency_id,
                'number':invoice.number,
                'rate':invoice.amount_total_company_signed/invoice.amount_total,
                })
        return data

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'partner_ids': self.read(['partner_ids'])[0]['partner_ids'], 
            'company_currency': self.env.user.company_id.currency_id.name,
            'invoice_state': self.read(['invoice_state'])[0]['invoice_state']})
        return self.env['report'].with_context(landscape=True).get_action(self, 'sg_forexcurrency_reports.report_accounttransaction', data=data)

    def export_excel(self):
        data = self.check_report()
        data = self.pre_print_report(data['data'])
        date_from = data['form'].get('date_from') and datetime.strptime(data['form']['date_from'], DF) or False
        data['form']['date_from'] = date_from and date_from.strftime('%d/%m/%Y') or False
        date_to = data['form'].get('date_to', False) and datetime.strptime(data['form']['date_to'], DF) or False
        data['form']['date_to'] = date_to and date_to.strftime('%d/%m/%Y') or False
        invoices = self._get_invoices(data['form']['partner_ids'], date_from, date_to, data['form']['invoice_state'],data['form']['result_selection'])
        output =  StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sheet1')
        row = 0
        col = 0
        bold_format = workbook.add_format({'bold':  1})
        right_format = workbook.add_format({'bold':1,'align':'right'})
        merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter'})

        if date_from:
            worksheet.write(row, col,  unicode('Start Date', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col,  data['form']['date_from'], bold_format)
            worksheet.set_column(row, col, 20)
            col += 2

        if date_to:
            worksheet.write(row, col,  unicode('End Date', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col,  data['form']['date_to'], bold_format)
            worksheet.set_column(row, col, 20)
        if date_from or date_to:
            row += 2
        col = 0
        
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
        col = 0
        row += 1
        for inv_key,inv_details in invoices.items(): 
            col = 0
            worksheet.write(row, col, inv_key[1], bold_format)
            worksheet.set_column(row, col, 20)
            col = 0
            row += 1
            for inv in inv_details:
                col = 0
                worksheet.write(row, col, '')
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['date'])
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['number'])
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['amount'])
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['currency_id'].name)
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['rate'])
                worksheet.set_column(row, col, 20)
                col += 1
                worksheet.write(row, col, inv['amount_company'])
                worksheet.set_column(row, col, 20)
                col += 1                
                row += 1
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({'name': 'Transaction.xlsx', 'datas_fname': 'Transaction.xlsx', 'datas': result})
        download_url = '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=' + str(attachment_id.id)
        return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
                "target": "self",
            }


