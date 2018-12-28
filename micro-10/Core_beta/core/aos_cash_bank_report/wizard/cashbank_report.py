# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class DailyReport(models.TransientModel):
    _name = "daily.report"
    _description = "Daily Report"
     
    date_from = fields.Date(string='Date From', default=lambda *a: time.strftime('%Y-%m-01'))
    date = fields.Date(string='Date to', default=lambda *a: time.strftime('%Y-%m-%d'))
    type = fields.Selection([('cash','Cash'), ('bank','Bank')], string='Type', required=False)
    display_type = fields.Selection([('summary','Summary'), ('detail','Detail')], 
                                        string='Display Type', required=False, default='summary') 
    daily_cashbank_ids = fields.One2many('daily.report.cashbank', 'daily_id', string='Daily Cash Line')
    
    @api.model
    def default_get(self, fields):        
        res = super(DailyReport, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        type = self._context.get('default_type')
        journal_obj = self.env['account.journal']
        account_obj = self.env['account.account']
        acc_cashbank_lines = []
        for acc_cb in journal_obj.sudo().search([('type','=',type)]):
            acc_cashbank_lines.append([0, 0, {
               'account_id': acc_cb.default_debit_account_id.id,
               }])        
        res['daily_cashbank_ids'] = acc_cashbank_lines
        return res
    
    @api.multi
    def xls_export(self):
        context = self._context
        res = {}
        if context.get('xls_export'):
            # we update form with display account value
            datas = {'ids': context.get('active_ids', [])}
            datas['model'] = 'daily.report'
            datas['form'] = self.read()[0]
            #used_context = self._build_contexts(datas)
            #print "===datas===",datas
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'cash.bank.report.xls',
                    'datas': datas
            }
    
class DailyReportCashBank(models.TransientModel):
    _name = "daily.report.cashbank"
    _description = "Daily Report Cash"
            
    name = fields.Char(string='Name', select=True)
    daily_id = fields.Many2one('daily.report', string='Daily Report')
    account_id = fields.Many2one('account.account', string='Account')
    amount = fields.Float(string='Amount Statement')
    notes = fields.Text('Notes')
