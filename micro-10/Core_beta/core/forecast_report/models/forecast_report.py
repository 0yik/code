# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import models, fields, api,_
from odoo.exceptions import Warning as UserWarning
import base64
import StringIO
from datetime import datetime
import xlsxwriter

class report_forecast_wizard(models.Model):
    _name = 'report.forecast'

    @api.model
    def _get_default_line(self):
        line_ids = self.env['report.forecast.line']
        accounts = self.env['account.account'].sudo().search([])
        for account in accounts:
            new_id = line_ids.new({
                'account_code': account.code,
                'account_name': account.name,
                'account_id': account.id,
            })
            line_ids += new_id
        return line_ids


    name = fields.Char()
    forecast_date_from = fields.Date('Forecast Period From')
    forecast_date_to = fields.Date('Forecast Period To')
    sample_month = fields.Selection([
        ('01','January'),
        ('02','February'),
        ('03','March'),
        ('04','April'),
        ('05','May'),
        ('06','June'),
        ('07','July'),
        ('08','August'),
        ('09','September'),
        ('10','October'),
        ('11','November'),
        ('12','December'),
    ])
    sample_year = fields.Selection([
        ('2018', '2018'),
        ('2017', '2017'),
        ('2016', '2016'),
        ('2015', '2015')])
    month_growth_year_from = fields.Date()
    month_growth_year_to = fields.Date()
    growth_ids = fields.One2many('report.forecast.line', 'forecast_id', default=_get_default_line)

    @api.onchange('month_growth_year_from','month_growth_year_to')
    def onchange_year_growth(self):
        if self.month_growth_year_from and self.month_growth_year_to:
            if int(self.month_growth_year_from[0:4]) > int(self.month_growth_year_to[0:4]):
                raise UserWarning(_("Month Growth Period is not suitable"))

    @api.multi
    def print_xls_report(self):
        data = self.get_data()
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        wb = workbook.add_worksheet('Forecast Report')
        filename = "forecast_report.xls"

        wb.set_column('F:G', 12)
        header_style = workbook.add_format({'fg_color':'#92D050','font_size' :11,'bold': 1,'border': 1,'align': 'center','valign': 'vcenter'})

        column_header_style = workbook.add_format({'bg_color':'#dc1b26','font_size' :11,'bold': 1,'border': 1,'align': 'center','valign': 'vcenter'})
        column_header_style1 = workbook.add_format({'bg_color':'#FFFF00','font_size' :11,'bold': 1,'border': 1,'align': 'center','valign': 'vcenter'})

        body_header_style = workbook.add_format({'font_size' :11,'bold': 0,'border': 0,'align': 'center','valign': 'vcenter'})



        wb.merge_range('F1:H1', self.env.user.company_id.name, header_style)
        # wb.set_row(1, 6, 80)

        wb.write(4, 1, 'Account Code', column_header_style)
        wb.set_column(4, 1, 20)

        wb.write(4,  2, 'Account Name', column_header_style)
        wb.set_column(4, 2, 20)

        wb.write(4,  3, 'Growth Rate', column_header_style)
        wb.set_column(4, 3, 20)

        forecast_date_from = datetime.strptime(self.forecast_date_from, "%Y-%m-%d")
        forecast_date_end = datetime.strptime(self.forecast_date_to, "%Y-%m-%d")
        forecast_date_from = forecast_date_from.strftime("%Y-%m-01")
        forecast_date_end = forecast_date_end.strftime("%Y-%m-01")
        forecast_date_from = datetime.strptime(forecast_date_from, "%Y-%m-%d")
        forecast_date_end = datetime.strptime(forecast_date_end, "%Y-%m-%d")
        count = 4
        while forecast_date_from <= forecast_date_end:
            wb.write(4,  count, forecast_date_from.strftime("%b-%y"), column_header_style1)
            wb.set_column(4, count, 20)

            count+=1
            forecast_date_from+=relativedelta(months=+1)
        count_row = 5
        count_col = False
        for line in self.growth_ids:
            count_col = 4
            forecast_date_from = datetime.strptime(self.forecast_date_from, "%Y-%m-%d")
            forecast_date_end = datetime.strptime(self.forecast_date_to, "%Y-%m-%d")
            forecast_date_from = forecast_date_from.strftime("%Y-%m-01")
            forecast_date_end = forecast_date_end.strftime("%Y-%m-01")
            forecast_date_from = datetime.strptime(forecast_date_from, "%Y-%m-%d")
            forecast_date_end = datetime.strptime(forecast_date_end, "%Y-%m-%d")
            account = line.account_id
            account_code = line.account_code
            account_name = line.account_name
            rate = line.growth_rate
            res = data[account.id]
            wb.write(count_row,  1,  account_code, body_header_style)
            wb.set_column(count_row, 1, 20)

            wb.write(count_row,  2,  account_name, body_header_style)
            wb.set_column(count_row, 2, 20)

            wb.write(count_row,  3,  str(rate) +'%', body_header_style)
            wb.set_column(count_row, 3, 20)

            while forecast_date_from <= forecast_date_end:
                wb.write(count_row,  count_col,res.get(forecast_date_from.strftime("%b-%y"), ""), body_header_style)
                wb.set_column(count_row, count_col, 20)

                count_col += 1
                forecast_date_from += relativedelta(months=+1)
            count_row+=1
        wb.write(count_row+1,  count_col and count_col-2 or 10, 'Printed on')
        wb.set_column(count_row+1, count_col and count_col-2 or 10, 20)

        wb.write(count_row+1, count_col and count_col-1 or 11, datetime.today().strftime("%d/%m/%Y"),column_header_style1)
        wb.set_column(count_row+1, count_col and count_col-1 or 11,  20)

        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': filename, 'datas_fname': 'forecase_report.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    @api.multi
    def get_data(self):
        results = {}
        for growth_line in self.growth_ids:
            account = growth_line.account_id
            results.update({
                account.id : {}
            })
            month_growth_matrix = {
                '01' : 0,
                '02' : 0,
                '03' : 0,
                '04' : 0,
                '05' : 0,
                '06' : 0,
                '07' : 0,
                '08' : 0,
                '09' : 0,
                '10' : 0,
                '11' : 0,
                '12' : 0,
            }
            month_growth_year_from = "%s-01-01" % self.month_growth_year_from[0:4]
            month_growth_year_to = "%s-12-31" % self.month_growth_year_to[0:4]
            self._cr.execute("SELECT line.account_id as account_id, account.name as aname, to_char(date_trunc('month', line.date),'yy-mm')"
                             "AS date_month, COALESCE(SUM(line.debit),0) - COALESCE(SUM(line.credit), 0) as balance FROM account_move_line as"
                             " line,account_account as account,account_move AS move WHERE account.id = %s and line.account_id = account.id AND move.id = line.move_id"
                             "  AND move.state in ('draft', 'posted') AND line.date <= '%s' AND line.date >= '%s' GROUP BY  "
                             "date_month,line.account_id, aname order by line.account_id, date_month asc" % (account.id,month_growth_year_to, month_growth_year_from))
            sql_result = self._cr.dictfetchall()
            balance_current_month = 0
            for row in sql_result:
                date_month = row['date_month']
                month = date_month.split('-')[1]
                # account_id = row['account_id']
                # account_name = row['aname']
                balance_previous_month, balance_current_month = balance_current_month, row['balance']
                if balance_previous_month == 0:
                    month_growth_matrix[month]+= 0
                    continue
                rate = ( balance_current_month - balance_previous_month ) / balance_previous_month
                month_growth_matrix[month] += rate
            distance_years_length = int(self.month_growth_year_to[0:4]) - int(self.month_growth_year_from[0:4]) + 1
            for key, val in month_growth_matrix.iteritems():
                month_growth_matrix[key] = month_growth_matrix[key]/distance_years_length
            sample_month = self.sample_month
            sample_year =  self.sample_year
            sample_date = '%s-%s-1' % (sample_year, sample_month)
            sample_end_of_month_of_sample_date = (datetime.strptime(sample_date,'%Y-%m-1') + relativedelta(months=+1)).strftime('%Y-%m-1')
            self._cr.execute(
                "SELECT line.account_id as account_id,  "
                "COALESCE(SUM(line.debit),0) - COALESCE(SUM(line.credit), 0) as balance FROM account_move_line as"
                " line,account_account as account,account_move AS move WHERE account.id = %s and line.account_id = account.id AND move.id = line.move_id"
                "  AND move.state in ('draft', 'posted') AND line.date < '%s' AND line.date >= '%s' GROUP BY  "
                "line.account_id" % (
                account.id, sample_end_of_month_of_sample_date, sample_date))
            sql_result = self._cr.dictfetchall()
            for row in sql_result:
                sample_balance = row['balance']
                forecast_date_from = datetime.strptime(self.forecast_date_from, "%Y-%m-%d")
                forecast_date_end = datetime.strptime(self.forecast_date_to, "%Y-%m-%d")
                forecast_date_from = forecast_date_from.strftime("%Y-%m-01")
                forecast_date_end = forecast_date_end.strftime("%Y-%m-01")
                forecast_date_from = datetime.strptime(forecast_date_from, "%Y-%m-%d")
                forecast_date_end = datetime.strptime(forecast_date_end, "%Y-%m-%d")
                sample_date = datetime.strptime(sample_date,"%Y-%m-1")
                loop_month_untill_end_of_forecase = sample_date + relativedelta(months=+1)
                previous_balance = sample_balance
                while loop_month_untill_end_of_forecase <= forecast_date_end:
                    current_balance = previous_balance + previous_balance * month_growth_matrix[loop_month_untill_end_of_forecase.strftime("%m")]
                    if loop_month_untill_end_of_forecase >= forecast_date_from:
                        results[account.id].update({
                            loop_month_untill_end_of_forecase.strftime("%b-%y")  :
                                current_balance
                        })
                    previous_balance = current_balance
                    loop_month_untill_end_of_forecase += relativedelta(months=+1)
            for key, val in results[account.id].iteritems():
                results[account.id][key] = results[account.id][key] + results[account.id][key] * growth_line.growth_rate / 100
        return results

class report_forecast_line(models.Model):
    _name = 'report.forecast.line'

    name = fields.Char()
    forecast_id = fields.Many2one('report.forecast')
    account_code = fields.Char('Account Code')
    account_name = fields.Char('Account Name')
    account_id = fields.Many2one('account.account', string='Account Name')
    growth_rate = fields.Float('Growth Rate')

class Account(models.Model):
    _inherit = 'account.account'

    @api.multi
    def name_get(self):
        if self._context.get('forecast_report'):
            res = []
            for account in self:
                res.append((account.id, account.name))
            return res
        else:
            return super(Account, self).name_get()