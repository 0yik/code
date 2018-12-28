# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.tools.misc import xlwt
from odoo.http import request

import base64
import unicodedata
import StringIO
import xlsxwriter
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class financial_ratio(models.Model):
    _name = "financial.ratio"

    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)

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
                res[row['id']] = row
        return res

    def check_financial_report(self):
	context = self.env.context
	res = self
	move_account = []
	lines = []
	dates = ''
	move_ids = []
        output =  StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sheet1')
        row = 0
        col = 0
        bold_format = workbook.add_format({'bold':  1})
    	result = base64.b64encode(output.read())
    	attachment_obj = self.env['ir.attachment']
    	attachment_id = attachment_obj.create({'name': 'Financial Ratio.xlsx', 'datas_fname': 'Financial Ratio.xlsx', 'datas': result})
    	download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
    	base_url = self.env['ir.config_parameter'].get_param('web.base.url')
	worksheet.write(row, col,  unicode('Financial Ratios Report', "utf-8"), bold_format)
    	worksheet.set_column(row, col, 20)
	row += 1

	worksheet.write(row, col,res.company_id.name or '',bold_format)
    	worksheet.set_column(row, col, 20)
    	row += 1
	if res.date_from or res.date_to:
		dates = '%s - %s' %(res.date_from, res.date_to)
		worksheet.write(row, col,dates or '',bold_format)
    		worksheet.set_column(row, col, 20)
    		row += 2
	else:
		row += 2

	worksheet.write(row, col,  unicode('Activity Ratios', "utf-8"), bold_format)
    	worksheet.set_column(row, col, 30)
	col += 1
	
	
	worksheet.write(row, col,  unicode('Value', "utf-8"), bold_format)
    	worksheet.set_column(row, col, 5)
	col += 1

	worksheet.write(row, col,  unicode('Formula', "utf-8"), bold_format)
    	worksheet.set_column(row, col, 60)
	row += 1
	col -= 2

	
	worksheet.write(row, col,  unicode('Receivables Turnover', "utf-8"))
    	worksheet.set_column(row, col, 30)

	row += 1

	worksheet.write(row, col,  unicode('Days of Sales Outstanding', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1
	
	worksheet.write(row, col,  unicode('Inventory Turnover', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('Days Of Inventory On Hand', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('Payables Turnover', "utf-8"),)
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('No. Of Days Of Payables', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('Total Asset Turnover', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('Fixed Asset Turnover', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('Working Capital Turnover', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1
	
	worksheet.write(row, col,  unicode('Liquidity Ratios', "utf-8"), bold_format)
    	worksheet.set_column(row, col, 30)
	col += 1
	
	
	worksheet.write(row, col,  unicode('Value', "utf-8"), bold_format)
    	worksheet.set_column(row, col, 5)
	col += 1

	worksheet.write(row, col,  unicode('Formula', "utf-8"), bold_format)
    	worksheet.set_column(row, col, 60)
	row += 1
	col -= 2

	worksheet.write(row, col,  unicode('Current Ratio', "utf-8"))
    	worksheet.set_column(row, col, 30)

	row += 1

	worksheet.write(row, col,  unicode('Quick Ratio', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1
	
	worksheet.write(row, col,  unicode('Cash Ratio', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('Return On Asset(ROA)', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('Operating Return On Assets', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('Return On Total Capital', "utf-8"))
    	worksheet.set_column(row, col, 30)
	row += 1

	worksheet.write(row, col,  unicode('Return On Equity', "utf-8"))
    	worksheet.set_column(row, col, 30)
	col += 2
	row -= 16

	worksheet.write(row, col,  unicode('Annual Sales/Average Receivables', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('365/Receivables Turnover', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('Cost of Goods Sold/Average Inventory', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('365/Inventory Turnover', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('Purchases/Average trades payable', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('356/Payables Turnover ratio', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('Revenue/Average Total Assets', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1
	
	worksheet.write(row, col,  unicode('Revenue/Average Net Fixed Asset', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('Revenue/Average Working Capital', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 2

	worksheet.write(row, col,  unicode('Current Assest/Current Liabilities', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('Cash + Marketable Securities + Receivables/Current Liabilities', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('Cash + Marketable Securities/Current Liabilities', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('Net Income/Average Total Assets', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('Operating Income/Average Total Assets OR EBIT/Average Total Assets', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('EBIT/Average Total Capital', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1

	worksheet.write(row, col,  unicode('Net Income/Average Total Equity', "utf-8"))
    	worksheet.set_column(row, col, 60)
	row += 1	

	company_name = self.env.user.company_id.id
	self.env.cr.execute("SELECT * FROM account_move_line WHERE company_id=%s" %(company_name))
	moves = self.env.cr.fetchall()
	for move in moves:
		account = self.env['account.move.line'].sudo().browse(move[0])
		if self.date_from and self.date_to:
			if account.date >= self.date_from and account.date <= self.date_to:
				move_account.append(account.id)
		else:
			if self.date_from and account.date >= self.date_from:
				move_account.append(account.id)
			if self.date_to and account.date <= self.date_to:
				move_account.append(account.id)
		if not self.date_from and not self.date_to:
			move_account.append(account.id)

	for m_id in move_account:
		if self.target_move == 'posted':
			move = self.env['account.move.line'].browse(m_id)
			if move.move_id.state == 'posted':
				move_ids.append(move.account_id.id)
		if self.target_move == 'all':
			move = self.env['account.move.line'].browse(m_id)
			if move.move_id.state in ['draft','posted']:
				move_ids.append(move.account_id.id)
	account_id = self.env['account.account'].sudo().search([('id', 'in', [account for account in move_ids])])
	account_balance = self._compute_account_balance(account_id)
	for account, value in account_balance.items():
	    flag = False
	    account_id = self.env['account.account'].sudo().search([('id', '=', account)])
	    vals = {
	        'name': account_id.code + ' ' + account_id.name,
		'company_id': account_id.company_id or False,
	        'balance': value['balance'],
                'type': 'account',
	        'account_type': account_id.internal_type,
		'type': account_id.user_type_id.name or False,
	    }
	    lines.append(vals)
	balance = 0.0
	asset_balance = 0.0	
	average_trades_payable = 0.0
	purchases_balance = 0.0
	liability_balance = 0.0
	current_asset_balance = 0.0
	non_current_asset_balance = 0.0
	fixed_asset_balance = 0.0
	net_income_balance = 0.0
	equity_balance = 0.0
	average_total_equity = 0.0
	average_trades_payable_balance = 0.0
	payables_turnover = 0.0
	revenue_balance = 0.0
	net_fixed_assets = 0.0
	no_of_days_payable = 0.0
	total_asset_turnover = 0.0
	fixed_asset_turnover = 0.0
	working_capital_turnover = 0.0
	current_ratio = 0.0
	return_on_asset = 0.0
	return_on_equity = 0.0
	values = {}
	for line in lines:
		if line['account_type'] == 'receivable':
			balance += line['balance']
			balance = balance
			#average_receivable = balance/2
		if line['type'] == 'Current Assets':
			asset_balance += line['balance']
			asset_balance = asset_balance
		if line['type'] == 'current_liability':
			liability_balance += line['balance']		
		if line['account_type'] == 'payable':
			purchases_balance += line['balance']
			purchases_balance = purchases_balance
		if line['account_type'] == 'payable':
			average_trades_payable += line['balance']
			average_trades_payable = average_trades_payable
			average_trades_payable_balance = average_trades_payable/2
				
		if line['type'] == 'Cost of Revenue':
			revenue_balance += line['balance']
			revenue_balance = revenue_balance
		if line['type'] == 'Current Assets':
			current_asset_balance += line['balance']
			current_asset_balance = current_asset_balance
		if line['type'] == 'Non-current Assets':
			non_current_asset_balance += line['balance']
			non_current_asset_balance = non_current_asset_balance
		
		if line['type'] == 'Fixed Assets':
			fixed_asset_balance += line['balance']
			fixed_asset_balance = fixed_asset_balance
			net_fixed_assets = fixed_asset_balance/2
		working_capital = asset_balance - liability_balance
		average_working_capital = working_capital/2
		if line['type'] == 'Income':
			net_income_balance += line['balance']
			net_income_balance = net_income_balance
		if line['type'] == 'Equity':
			equity_balance += line['balance']
			equity_balance = equity_balance
			average_total_equity = equity_balance/2
		if average_trades_payable_balance != 0.0:
			payables_turnover = purchases_balance/average_trades_payable_balance
		else:
			payables_turnover = purchases_balance	
		if payables_turnover != 0.0:
			no_of_days_payable = 356/payables_turnover
		else:
			no_of_days_payable = payables_turnover
		average_total_assets_balance =  (current_asset_balance + non_current_asset_balance)/2

		if average_total_assets_balance == 0.0:
			total_asset_turnover = revenue_balance
		else:
			total_asset_turnover = revenue_balance/average_total_assets_balance
		if net_fixed_assets != 0.0:
			fixed_asset_turnover = revenue_balance/net_fixed_assets
		else:
			fixed_asset_turnover = revenue_balance
		if average_working_capital != 0.0:
			working_capital_turnover = revenue_balance/average_working_capital
		else:
			working_capital_turnover = revenue_balance
		if liability_balance != 0.0:
			current_ratio = asset_balance/liability_balance
		else:
			current_ratio = asset_balance
		if average_total_assets_balance != 0.0:
			return_on_asset = net_income_balance/average_total_assets_balance
		else:
			return_on_asset = net_income_balance
		if average_total_equity != 0.0:
			return_on_equity = net_income_balance/average_total_equity
		else:
			return_on_equity = net_income_balance
	worksheet.write(9, 1, payables_turnover)
	worksheet.write(10, 1, no_of_days_payable)
	worksheet.write(11, 1, total_asset_turnover)
	worksheet.write(12, 1, fixed_asset_turnover)
	worksheet.write(13, 1, working_capital_turnover)
	worksheet.write(15, 1, current_ratio)	
	worksheet.write(18, 1, return_on_asset)
	worksheet.write(21, 1, return_on_equity)

	workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({'name': 'Financial Ratio.xlsx', 'datas_fname': 'Financial Ratio.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

    	return {
        	"type": "ir.actions.act_url",
        	"url": str(base_url) + str(download_url),
        	"target": "self",
    	}
