import time

from odoo.report import report_sxw
from odoo.tools.translate import _
from odoo.osv import osv
from common_report_header import common_report_header
from odoo.api import Environment

class CashBankReport(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(CashBankReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            #'get_accounts_other': self._get_accounts_other,
            'get_accounts': self._get_accounts,
            'get_lines': self._get_lines,
        })
        self.context = context
    
    def _get_accounts(self, data):
        self.env = Environment(self.cr, self.uid, self.context)
        lines = []
        init_balance = True
        sortby = 'sort_date'
        display_account = 'all'
        daily_ids = data['form']['daily_cashbank_ids']
        account_ids = self._get_account_daily_report(daily_ids)
        accounts = self.env['account.account'].browse(account_ids)
        accounts_res = []
        accounts_res = self._get_account_move_init_balance(data['form'], accounts, init_balance, sortby, display_account)
        #print "=accounts_res==",accounts_res
        return accounts_res
    
    def _get_lines(self, data, account_init, account_sum):
        accounts_lines = self._get_account_move_counter_part(data['form'], account_init, account_sum)
        return accounts_lines