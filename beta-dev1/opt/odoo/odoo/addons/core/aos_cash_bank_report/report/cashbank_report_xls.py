# -*- coding: utf-8 -*-
# Copyright 2010 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import time
import xlwt

from report_xls import ReportXls

from cashbank_report import CashBankReport

from odoo.tools.translate import _

_column_sizes = [
    ('A', 25),
    ('B', 25),
    ('C', 25),     
    ('D', 25),     
    ('E', 25),     
    ('F', 30),     
    ('G', 25),     
    ('H', 25),     
    ('I', 25),          
]

class cash_bank_xls(ReportXls):
    column_sizes = [x[1] for x in _column_sizes]
    no_ind = 0
    
    def get_no_index(self):
        self.set_no_index()
        return self.no_ind
    
    def set_no_index(self):
        self.no_ind += 1
        return True
            
    def generate_xls_report(self, _p, _xs, data, objects, wb):
#         print "--------generate_xls_report----------",_p.company.partner_id.name
#         c = parser.localcontext['company']
        for cash_account in _p.get_accounts(data):            
            #row_pos = self.xls_write_row(ws, row_pos, row_data, set_column_size=True)
            # Header Table
            cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all']
            cell_non_format = _xs['bold'] + _xs['borders_all']
            cell_style = xlwt.easyxf(cell_format)
            cell_title_style = xlwt.easyxf(cell_non_format)
            cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
            cell_style_left = xlwt.easyxf(cell_format, num_format_str='#,##0.00;(#,##0.00)')
            
            # Column Title Row
            cell_format = _xs['bold']
            c_title_cell_style = xlwt.easyxf(cell_format)
    
            # Column Header Row
            cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
            c_hdr_cell_style = xlwt.easyxf(cell_format)
            c_hdr_cell_style_right = xlwt.easyxf(cell_format + _xs['right'])
            c_hdr_cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
            c_hdr_cell_style_decimal = xlwt.easyxf(cell_format + _xs['right'],num_format_str=ReportXls.decimal_format)
    
            # Column Initial Balance Row
            cell_format = _xs['italic'] + _xs['borders_all']
            c_init_cell_style = xlwt.easyxf(cell_format)
            c_init_cell_style_decimal = xlwt.easyxf(cell_format + _xs['right'],num_format_str=ReportXls.decimal_format)
            
            # cell styles for ledger lines
            ll_cell_format = _xs['borders_all']
            ll_cell_top_format = _xs['borders_top_bottom']
            ll_cell_style = xlwt.easyxf(ll_cell_format)
            ll_cell_style_center = xlwt.easyxf(ll_cell_format + _xs['center'])
            ll_cell_style_left = xlwt.easyxf(num_format_str='#,##0.00;(#,##0.00)')
            ll_cell_style_left_percent = xlwt.easyxf(_xs['bold'] + ll_cell_top_format, num_format_str='0%')
            ll_cell_style_date = xlwt.easyxf(ll_cell_format + _xs['left'],num_format_str=ReportXls.date_format)
            ll_cell_style_decimal = xlwt.easyxf(ll_cell_format + _xs['right'],num_format_str=ReportXls.decimal_format)
            
            tot_cell_format = _xs['bold']
            #c_tot_cell_style = xlwt.easyxf(tot_cell_format)
            ll_tot_cell_style_left = xlwt.easyxf(tot_cell_format, num_format_str='#,##0.00;(#,##0.00)')          
            #for cash_line in cash_account['move_lines']:
            ws = wb.add_sheet(('%s' % cash_account['name']))
            ws.panes_frozen = True
            ws.remove_splits = True
            ws.portrait = 0  # Landscape
            ws.fit_width_to_pages = 1
            row_pos = 0
            # set print header/footer
            ws.header_str = self.xls_headers['standard']
            ws.footer_str = self.xls_footers['standard']
            
            header_name = _p.company.partner_id.name
            c_specs = [('report_name', 1, 0, 'text', header_name)]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_title_style)
            #for header title 2
            c_specs = [('title_name', 1, 0, 'text', '%s' % cash_account['name'])]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_title_style)
            #date_from
            df = _('Period') + ': ' + _p.formatLang(data['form']['date_from'], date=True) + ' to ' + _p.formatLang(data['form']['date'], date=True)

            c_specs = [('df', 1, 0, 'text', df)]

            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_title_style)
            # write empty row to define column sizes
                
            c_sizes = self.column_sizes
            c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None) for i in range(0, len(c_sizes))]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, set_column_size=True)
            
            c_spec_first = [
                ('acd', 1, 0, 'text', '%s' % cash_account['name']),
                ('acp', 1, 0, 'text', 'Account Counter Part')]
            c_spec_middle = []
            if data['form']['display_type'] == 'detail':
                c_spec_middle = [
                    ('dsc', 1, 0, 'text', 'Description'),
                    ('dt', 1, 0, 'text', 'Date')]
            c_spec_last = [
                ('db', 1, 0, 'text', 'Debit'),
                ('cr', 1, 0, 'text', 'Credit'),
                ('bl', 1, 0, 'text', 'Balance')]
            c_specs = c_spec_first + c_spec_middle + c_spec_last
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, cell_style_center)              
            c_spec_first = [
                ('acc_cash', 1, 0, 'text', cash_account['name']),
                ('acc_counter', 1, 0, 'text', 'Starting Balance')]
            c_spec_middle = []
            if data['form']['display_type'] == 'detail':
                c_spec_middle = [
                    ('name_counter', 1, 0, 'text', ''),
                    ('date_counter', 1, 0, 'text', '')]
            c_spec_last = [
                ('dbc', 1, 0, 'number', cash_account['debit']),
                ('crc', 1, 0, 'number', cash_account['credit']),
                ('blc', 1, 0, 'number', cash_account['balance'])]
            c_specs = c_spec_first + c_spec_middle + c_spec_last
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, ll_tot_cell_style_left)
            #========================UNTUK INIT GL CASH===============================
            for cash_line in cash_account['move_lines']:
                cash_progress = debit_progress = credit_progress = 0.0
                for line_co_cash in _p.get_lines(data, cash_account['id'], cash_line['balance']):
                    c_spec_first = [
                        ('acc_cash', 1, 0, 'text', ''),
                        ('acc_counter', 1, 0, 'text', line_co_cash['lref'])]
                    c_spec_middle = []
                    if data['form']['display_type'] == 'detail':
                        c_spec_middle = [
                            ('lname_counter', 1, 0, 'text', line_co_cash['move_name']),
                            ('ldate_counter', 1, 0, 'text', _p.formatLang(line_co_cash['ldate'], date=True))]
                    c_spec_last = [
                        ('dbc', 1, 0, 'number', line_co_cash['debit']),
                        ('crc', 1, 0, 'number', line_co_cash['credit']),
                        ('blc', 1, 0, 'number', line_co_cash['progress'])]
                    c_specs = c_spec_first + c_spec_middle + c_spec_last
                    debit_progress += line_co_cash['debit']
                    credit_progress += line_co_cash['credit']
                    cash_progress = line_co_cash['progress']
                    row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                    row_pos = self.xls_write_row(ws, row_pos, row_data, ll_cell_style_left)
                #Total
                c_spec_first = [
                    ('col', 1, 0, 'text', ''),
                    ('col', 1, 0, 'text', '')]
                c_spec_middle = []
                if data['form']['display_type'] == 'detail':
                    c_spec_middle = [
                        ('col', 1, 0, 'text', ''),
                        ('col', 1, 0, 'text', '')]
                c_spec_last = [
                    ('col', 1, 0, 'text', ''),
                    ('col', 1, 0, 'text', ''),
                    ('prgs', 1, 0, 'text', ''),
                ]
                c_specs = c_spec_first + c_spec_middle + c_spec_last
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_tot_cell_style_left)
                #Selisih/Rekonsiliasi
                c_spec_first = [
                    ('col', 1, 0, 'text', ''),
                    ('sr', 1, 0, 'text', 'Total Debits')]
                c_spec_middle = []
                if data['form']['display_type'] == 'detail':
                    c_spec_middle = [
                        ('col', 1, 0, 'text', ''),
                        ('col', 1, 0, 'text', '')]
                c_spec_last = [
                    ('col', 1, 0, 'text', ''),
                    ('col', 1, 0, 'text', ''),
                    ('prgs', 1, 0, 'number', debit_progress)]
                c_specs = c_spec_first + c_spec_middle + c_spec_last
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_tot_cell_style_left)
                #Alasan Selisih
                c_spec_first = [
                    ('col', 1, 0, 'text', ''),
                    ('sr', 1, 0, 'text', 'Total Credits')]
                c_spec_middle = []
                if data['form']['display_type'] == 'detail':
                    c_spec_middle = [
                        ('col', 1, 0, 'text', ''),
                        ('col', 1, 0, 'text', '')]
                c_spec_last = [
                    ('col', 1, 0, 'text', ''),
                    ('col', 1, 0, 'text', ''),
                    ('prgs', 1, 0, 'number', credit_progress)]
                c_specs = c_spec_first + c_spec_middle + c_spec_last
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_tot_cell_style_left)   
                #Saldo Fisik/Rekening
                c_spec_first = [
                    ('col', 1, 0, 'text', ''),
                    ('sfr', 1, 0, 'text', 'Ending Balance')]
                c_spec_middle = []
                if data['form']['display_type'] == 'detail':
                    c_spec_middle = [
                        ('col', 1, 0, 'text', ''),
                        ('col', 1, 0, 'text', '')]
                c_spec_last = [
                    ('col', 1, 0, 'text', ''),
                    ('col', 1, 0, 'text', ''),
                    ('prgs', 1, 0, 'number', cash_progress)]
                c_specs = c_spec_first + c_spec_middle + c_spec_last
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_tot_cell_style_left)
                
                row_pos += 1      
        row_pos += 1
        pass

cash_bank_xls('report.cash.bank.report.xls',
                  'daily.report',
                  parser=CashBankReport)        

