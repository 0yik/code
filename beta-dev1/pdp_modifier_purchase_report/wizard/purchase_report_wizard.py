from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import base64
from cStringIO import StringIO
#import xlsxwriter #this package is not supported form me that's a reasone in local we use  import xlwt and replace for xlsxwriter
import xlwt
import csv
import os.path
import pytz

class GlobalPurchaseReportWizard(models.TransientModel):
    _name = "global.purchase.report.wizard"

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Supplier')
    format = fields.Selection([('pdf','PDF'),('xls','XLS')], string="Format", default='pdf')

    @api.multi
    def print_report(self):
        if self.format=='pdf':
            return self.env['report'].get_action(self, 'pdp_modifier_purchase_report.report_global_purchaseorder')
        else:
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('sheet1') 
            row = 1
            col = 0
            bold_format = xlwt.easyxf('font: bold on;')
            right_format = xlwt.easyxf('font: bold on; align: horiz right;')
            merge_format = xlwt.easyxf('font: bold on; border: bottom medium; align: vertical center, horizontal center;')
            font_size_format = xlwt.easyxf('font: bold on;')
            po_title = xlwt.easyxf('align: vertical center, horizontal center; font: bold on;font:height 280;border: top medium, bottom medium, right medium, left medium;')
            current_time = datetime.now()
            current_time_utc = pytz.timezone('UTC').localize(current_time, is_dst=False)
            if not self.env.user.tz:
                raise UserError(_("Pleas select Time zone in Users"))                
            current_time = current_time_utc.astimezone(pytz.timezone(self.env.user.tz))
            current_time = str(current_time)[:19]
            current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %I:%M %p')
            worksheet.write_merge(row, row, col, col+1, unicode('Printed : ' + str(current_time), "utf-8"), font_size_format)
            new_row = row + 1
            worksheet.write_merge(row, new_row, 3, 5, unicode('GLOBAL PURCHASE ORDER', "utf-8"), po_title)
            row+=2
            col = 3
            worksheet.write_merge(row, row, col, col+2, unicode('Period : ' + self.from_date + ' 00:00' + ' Upto ' + self.to_date + ' 23:59', "utf-8"), xlwt.easyxf('align: vertical center, horizontal center; font: bold on;'))
            row+=2
            
            #get purchase order      
            domain = [('date_order','>=',self.from_date),('date_order','<=',self.to_date)]      
            orders = self.env['purchase.order'].search(domain)
            data = {}
            for order in orders:
                if data.get(order.pricelist_id):
                    data[order.pricelist_id].append(order)
                else:
                    data[order.pricelist_id] = [order]
            for pricelist,orders in data.iteritems():
                custom_discount_rate = 0
                price_total = 0
                col=0
                title_format = xlwt.easyxf('font: bold on;font:height 220;border: top medium;border: bottom medium; border: right medium; border: left medium;')
                
                #Title of table
                worksheet.write(row, col, unicode('State', "utf-8"), title_format)
                col+=1
                worksheet.write(row, col, unicode('Date', "utf-8"), title_format)
                col+=1
                worksheet.write(row, col, unicode('Transaction', "utf-8"), title_format)
                worksheet.col(col).width = 256 * 14
                col+=1
                worksheet.write(row, col, unicode('Ref No.', "utf-8"), title_format)
                col+=1
                worksheet.write(row, col, unicode('Supplier', "utf-8"), title_format)
                worksheet.col(col).width = 256 * 28 #28 characters wide (-ish)
                col+=1
                worksheet.write(row, col, unicode('Term', "utf-8"), title_format)
                col+=1
                worksheet.write(row, col, unicode('Amount Total', "utf-8"), title_format)
                worksheet.col(col).width = 256 * 14#14 characters wide (-ish)
                row += 1
                #currency_id
                col=0
                worksheet.write(row, col, unicode('Currency:', "utf-8"), xlwt.easyxf('font: color blue; font: bold on;border: bottom medium;border: top medium;border: right medium; border: left medium;font:height 220;'))
                worksheet.write_merge(row, row, 1, 6, pricelist.currency_id.name, xlwt.easyxf('font: color blue; font: bold on;border: bottom medium;border: top medium;border: right medium; border: left medium;font:height 220;'))
                #Table Data
                total_define_col = 0
                for order in orders:
                    row += 1
                    col=0
                    date_order = datetime.strptime(order.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                    worksheet.write(row, col, order.state)
                    col+=1
                    worksheet.write(row, col, date_order)
                    col+=1
                    worksheet.write(row, col, order.name)
                    col+=1
                    if order.partner_ref:
                        worksheet.write(row, col, order.partner_ref)
                    col+=1
                    worksheet.write(row, col, order.partner_id.name)
                    col+=1
                    if order.payment_term_id.name:
                        worksheet.write(row, col, order.payment_term_id.name)
                    col+=1
                    #if order.amount_total:
                    worksheet.write(row, col, order.amount_total)
                    price_total += order.amount_total
                    total_price_col = col
                row += 1
                col=0
                #Grand Total of data
                worksheet.write_merge(row, row, col ,col+5, 'Total'+ ' ' + pricelist.currency_id.name, xlwt.easyxf('font: bold on; border: top medium;border: bottom medium; border: right medium; border: left medium;'))
                worksheet.write(row,total_price_col, price_total, xlwt.easyxf('font: bold on; border: top medium;border: bottom medium; border: right medium; border: left medium; pattern: pattern solid, fore_colour yellow;'))
                row += 3
            
            fp = StringIO()
            workbook.save(fp)
            
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            attachment_obj = self.env['ir.attachment']
            attachment_id = attachment_obj.create(
                {'name': 'GlobalPurchaseOrder.xls', 'datas_fname': 'GlobalPurchaseOrder.xlsx', 'datas': base64.encodestring(fp.getvalue())})
            fp.close()
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
        orders = self.env['purchase.order'].search(domain)
        data = {}
        result = {}
        for order in orders:
            if data.get(order.pricelist_id):
                data[order.pricelist_id].append(order)
            else:
                data[order.pricelist_id] = [order]
        for pricelist,orders in data.iteritems():
            result[pricelist.currency_id.name] = {}
            custom_discount_rate = 0
            price_tax = 0
            price_total = 0
            records = []
            
            for order in orders:
                vals={}
                date_order = datetime.strptime(order.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                vals['state'] = order.state
                vals['date'] = date_order
                vals['transaction'] = order.name
                vals['ref_no'] = order.partner_ref or False
                vals['supplier'] = order.partner_id.name
                vals['term'] = order.payment_term_id.name or False
                vals['amount_total'] = order.amount_total
                vals['company_id'] = order.company_id
                records.append(vals)
            result[pricelist.currency_id.name] = records
        return result
