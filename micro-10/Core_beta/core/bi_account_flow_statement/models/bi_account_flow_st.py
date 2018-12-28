# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api
from datetime import datetime, date
import datetime

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class ChartfAccount(models.Model):
    _inherit = 'account.account'

    cash_flow_type = fields.Selection([('operating','Operating Activities'),('invest','Investing Activities'),('finance','Financial Activities')], 'Cash Flow Type')
    finance_report = fields.Many2one('account.financial.report','Financial Report')

class AccountCashFlow(models.TransientModel):
    _name = 'account.cashflow'

    account_report = fields.Many2one('account.financial.report', 'Account Report', required=True, default=lambda self: self.env['account.financial.report'].search([('name','=', 'Cash Flow Statement')]))
    start_amount = fields.Float('Cash Initial Balance')
    target_moves = fields.Selection([('all_posted','All Posted Entries'),('all','All Entries')], 'Target Moves')
    display_dt_cr = fields.Boolean('Display Debit Credit Columns')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    for_period = fields.Date('For the Period/Year Ending')
    enable_comparison = fields.Boolean('Enable Comparison')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env['res.company']._company_default_get('account.account'))
    cashflow_cal_id = fields.Many2one('account.cash.flow', 'Cashflow')
    #generated_by = fields.Many2one('res.users', string="CONTADOR", default=lambda self: self.env.user, required=True)
    #represented_by = fields.Many2one('res.users', string="REPRESENTANTE LEGAL", required=True)
    #auditor = fields.Many2one('res.users', string="AUDITOR", required=True)

    @api.multi
    def check_report_cashflow(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])
        return self.env['report'].get_action(self, 'bi_account_flow_statement.report_account_cashflow', data=data)
        
    
    @api.multi
    def make_excel(self,report_data,data):
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Cash Flow Statement")
        style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
        style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
        title = "Cash Flow Statement"
        style = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black;")
        worksheet.write_merge(0, 1, 0, 6,title, style = style_title)
        #worksheet.col.width = 1000
        row = 3
        col = 0
        if not data['display_dt_cr']:
 
            worksheet.write(4,0,['Target Moves'], style=style_table_header)
            worksheet.write(4,2,['Cash at the beginning of the year'], style=style_table_header)
            worksheet.write(4,4,['Start Date'], style=style_table_header)
            worksheet.write(4,6,['End Date'], style=style_table_header)
            worksheet.write(5,0,self.target_moves, style=style)
            worksheet.write(5,2,self.start_amount, style=style)
            worksheet.write(5,4,self.start_date, style=style)
            worksheet.write(5,6,self.end_date, style=style)
            worksheet.write(7,col,['Name'], style=style_table_header)
            worksheet.write(7,2,['Accounting Activity'], style=style_table_header)
            worksheet.write(7,6,['Balance'], style=style_table_header)

            col = 0
            row+=5
            for record in report_data:
                
                if record.get('account_activity_rep') and record.get('account_activity'):
                    col = 0
                    row+=1
      
                    worksheet.write(row,col,record.get('account_id'), style=style)
                    col+=2
                    worksheet.write(row,col,record.get('account_activity_rep'), style=style)
                    col+=4
                    worksheet.write(row,col,record.get('amount_dt') or record.get('amount_cr'), style=style)
            
        if data['display_dt_cr']:

            worksheet.write(4,0,['Target Moves'], style=style_table_header)
            worksheet.write(4,2,['Cash at the beginning of the year'], style=style_table_header)
            worksheet.write(4,4,['Start Date'], style=style_table_header)
            worksheet.write(4,6,['End Date'], style=style_table_header)
            worksheet.write(5,0,self.target_moves, style=style)
            worksheet.write(5,2,self.start_amount, style=style)
            worksheet.write(5,4,self.start_date, style=style)
            worksheet.write(5,6,self.end_date, style=style)
            worksheet.write(7,col,['Name'], style=style_table_header)
            worksheet.write(7,2,['Accounting Activity'], style=style_table_header)
            worksheet.write(7,3,['Debit'], style=style_table_header)
            worksheet.write(7,4,['Credit'], style=style_table_header)
            worksheet.write(7,6,['Balance'], style=style_table_header)

            col = 0
            row+=5
            for record in report_data:

                if record.get('account_activity_rep') and record.get('account_activity'):

                    col = 0
                    row+=1
                           
                    worksheet.write(row,col,record.get('account_id'), style=style)
                    col+=2
                    worksheet.write(row,col,record.get('account_activity_rep'), style=style)
                    col+=1
                    worksheet.write(row,col,record.get('amount_dt'), style=style)
                    col+=1
                    worksheet.write(row,col,record.get('amount_cr'), style=style)
                    col+=2
                    worksheet.write(row,col,record.get('amount_dt') - record.get('amount_cr'), style=style)
        
        
        
        file_data = cStringIO.StringIO()
        workbook.save(file_data)
	wiz_id = self.env['account.cashflow.save.wizard'].create({
		'state': 'get',
		'data': base64.encodestring(file_data.getvalue()),
		'name': 'Account Cashflow Statement.xls'
	})
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Account Cashflow Save Form',
            'res_model': 'account.cashflow.save.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }

    @api.multi
    def print_excel(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['start_date', 'end_date','display_dt_cr'])[0]
        #used_context = self._build_contexts(data)
        #data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        #comparison_context = self._build_comparison_context(data)
        #data['form']['comparison_context'] = comparison_context
        data.update({'type':'excel'})
        report_data = self.env['report.bi_account_flow_statement.report_account_cashflow'].button_calculate_rep(data['form'])
        return self.make_excel(report_data,data['form'])


class AccountCashFlow1(models.AbstractModel):
    _name = 'report.bi_account_flow_statement.report_account_cashflow'

    @api.multi
    def button_calculate_rep(self, data):
        acc_journal_obj = self.env['account.move.line']
        account_obj = self.env['account.account']
      
        pos = []
        result1 = {}
        
        if data['start_date'] and data['end_date']:
            date_between = acc_journal_obj.search([('date','>=',data['start_date'] + ' 00:00:00'),('date_maturity','<=',data['end_date'] + ' 23:59:59')])
        else:
            date_between = acc_journal_obj.search([])
    
        for acc in account_obj.search([]):
            move_line = acc_journal_obj.search([('id','in', map(int, date_between)),('account_id','=',acc.id)])
            debit_val = 0.0
            credit_val = 0.0
            for line in move_line:

                debit_val += line.debit 
                credit_val += line.credit

            if move_line:
                result1 = {
                    'amount_dt': debit_val,
                    'amount_cr': credit_val,
                    'account_id': acc.name,
                    'account_activity_rep': acc.finance_report.name,
                    'account_activity': acc.cash_flow_type,
                    'account_report': acc.finance_report.name, 
                }
                pos.append(result1)

        if pos:
            return pos
        else:
            return {}

    @api.model
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        report_lines = self.button_calculate_rep(data.get('form'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            #'time': time,
            'button_calculate_rep': report_lines,
        }
        return self.env['report'].render('bi_account_flow_statement.report_account_cashflow', docargs)
    
