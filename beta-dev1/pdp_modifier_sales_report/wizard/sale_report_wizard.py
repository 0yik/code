from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

import base64
import StringIO
import xlsxwriter
import csv
import os.path
import pytz

class GlobalSaleReportWizard(models.TransientModel):
    _name = "global.sale.report.wizard"

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    format = fields.Selection([('pdf','PDF'),('xls','XLS')], string="Format", default='pdf')

    @api.multi
    def print_report(self):
        if self.format=='pdf':
            return self.env['report'].get_action(self, 'pdp_modifier_sales_report.report_global_saleorder')
        else:
            output = StringIO.StringIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Sheet1')
            row = 1
            col = 0
            bold_format = workbook.add_format({'bold': 1})
            right_format = workbook.add_format({'bold': 1, 'align': 'right'})
            merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
            font_size_format = workbook.add_format()
            font_size_format.set_font_size(9)
            current_time = datetime.now()
            current_time_utc = pytz.timezone('UTC').localize(current_time, is_dst=False)
            current_time = current_time_utc.astimezone(pytz.timezone(self.env.user.tz))
            current_time = str(current_time)[:19]
            current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %I:%M %p')
            worksheet.write(row, col, unicode('Printed : ' + str(current_time), "utf-8"), font_size_format)
            col+=4
            bold_format.set_font_size(12)
            worksheet.write(row, col, unicode('GLOBAL SALES ORDER CUSTOMER', "utf-8"), bold_format)
            row+=1
            worksheet.write(row, col, unicode('Period : ' + self.from_date + ' 00:00' + ' Upto ' + self.to_date + ' 23:59', "utf-8"), font_size_format)
            row+=2
            col=0
            title_format = workbook.add_format({'bold': 1})
            title_format.set_font_size(11)
            worksheet.write(row, col, unicode('Date', "utf-8"), title_format)
            worksheet.write(row, col+1, unicode('Transaction', "utf-8"), title_format)
            worksheet.write(row, col+2, unicode('Customer', "utf-8"), title_format)
            worksheet.write(row, col+3, unicode('Term', "utf-8"), title_format)
            worksheet.write(row, col+4, unicode('Total', "utf-8"), title_format)
            worksheet.write(row, col+5, unicode('Discount', "utf-8"), title_format)
            worksheet.write(row, col+6, unicode('Tax', "utf-8"), title_format)
            worksheet.write(row, col+7, unicode('Net Total', "utf-8"), title_format)
            orders = self.get_order_details()
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0
            for order in orders:
                row+=1
                date_order = datetime.strptime(order.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                worksheet.write(row, col, date_order)
                worksheet.write(row, col+1, order.name)
                worksheet.write(row, col+2, order.partner_id.name)
                worksheet.write(row, col+3, order.payment_term_id.name)
                worksheet.write(row, col+4, order.amount_untaxed)
                worksheet.write(row, col+5, order.amount_discount)
                worksheet.write(row, col+6, order.amount_tax)
                worksheet.write(row, col+7, order.amount_total)
                amount_untaxed+=order.amount_untaxed
                amount_discount+=order.amount_discount
                amount_tax+=order.amount_tax
                amount_total+=order.amount_total
            row+=1
            total_format = workbook.add_format({'bg_color': '#D3D3D3','bold': 1})
            worksheet.write(row, col, "Total", total_format)
            worksheet.write(row, col+4, amount_untaxed, total_format)
            worksheet.write(row, col+5, amount_discount, total_format)
            worksheet.write(row, col+6, amount_tax, total_format)
            worksheet.write(row, col+7, amount_total, total_format)
            workbook.close()
            output.seek(0)
            result = base64.b64encode(output.read())
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            attachment_obj = self.env['ir.attachment']
            attachment_id = attachment_obj.create(
                {'name': 'GlobalSalesOrderCustomer.xls', 'datas_fname': 'GlobalSalesOrderCustomer.xlsx', 'datas': result})
            download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
            return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
            }

    @api.multi
    def get_order_details(self):
        data = {}
        domain = [('date_order','>=',self.from_date),('date_order','<=',self.to_date)]
        if self.partner_id:
            domain.append(('partner_id','=',self.partner_id.id))
        return self.env['sale.order'].search(domain)
