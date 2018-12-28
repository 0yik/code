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

class SalesReporsWizard(models.TransientModel):
    _name = "sales.reports.wizard"

    report = fields.Selection([('SalesOrderPerCustomer','Sales Order Per Customer'),
                               ('SalesOrderCustomerPerItem','Sales Order Customer Per Item'),
                               ('SalesOrderCustomerRealization','Sales Order Customer Realization')], 
                              string="Report")
    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    category_id = fields.Many2one('product.category', string="Category")
    format = fields.Selection([('pdf','PDF'),('xls','XLS')], string="Format", default='pdf')
    movement = fields.Selection([('discontinue','Discontinue'),('running','Running'),('slow','Slow')])

    @api.multi
    def print_report(self):
        if self.format=='pdf':
            
            if self.report == 'SalesOrderPerCustomer':
                return self.env['report'].get_action(self, 'pdp_modifier_sales_report.report_saleorder_per_customer')

            elif self.report == 'SalesOrderCustomerPerItem':
                return self.env['report'].get_action(self, 'pdp_modifier_sales_report.report_saleorder_per_item')

            elif self.report == 'SalesOrderCustomerRealization':
                return self.env['report'].get_action(self, 'pdp_modifier_sales_report.report_saleorder_realization')
        
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
            if self.report=='SalesOrderPerCustomer':
                report_name = 'Sales Order Per Customer'
            elif self.report=='SalesOrderCustomerPerItem':
                report_name = 'Sales Order Customer Per Item'
            else:
                report_name = 'Sales Order Customer Realization'
            worksheet.write(row, col, report_name, bold_format)
            row+=1
            worksheet.write(row, col, unicode('Period : ' + self.from_date + ' 00:00' + ' Upto ' + self.to_date + ' 23:59', "utf-8"), font_size_format)
            row+=2
            col=0
            title_format = workbook.add_format({'bold': 1})
            total_format = workbook.add_format({'bg_color': '#D3D3D3','bold': 1})
            title_format.set_font_size(11)

            if self.report=='SalesOrderPerCustomer':
                return self.print_so_per_customerreport(output,worksheet, workbook, title_format, total_format, bold_format, row, col)
            elif self.report=='SalesOrderCustomerPerItem':
                return self.print_so_per_itemreport(output, worksheet, workbook, title_format, total_format, bold_format, row, col)
            else:
                return self.print_so_realizationreport(output, worksheet, workbook, title_format, total_format, bold_format, row, col)

    @api.multi
    def print_so_per_customerreport(self, output, worksheet, workbook, title_format, total_format, bold_format, row, col):
        worksheet.write(row, col, unicode('Date', "utf-8"), title_format)
        worksheet.write(row, col+1, unicode('SOD No', "utf-8"), title_format)
        worksheet.write(row, col+2, unicode('Item Code', "utf-8"), title_format)
        worksheet.write(row, col+3, unicode('Item Name', "utf-8"), title_format)
        worksheet.write(row, col+4, unicode('Qty', "utf-8"), title_format)
        worksheet.write(row, col+5, unicode('Price', "utf-8"), title_format)
        worksheet.write(row, col+6, unicode('Disc', "utf-8"), title_format)
        worksheet.write(row, col+7, unicode('Tax', "utf-8"), title_format)
        worksheet.write(row, col+8, unicode('Total', "utf-8"), title_format)
        orders = self.get_orders()
        amount_discount = 0
        amount_tax = 0
        amount_total = 0
        amount_untaxed = 0
        data = {}
        for order in orders:
            if data.get(order.partner_id):
                data[order.partner_id].append(order)
            else:
                data[order.partner_id] = [order]
        color = workbook.add_format({'color': '#0B0BA9','bold': 1})
        for partner,orders in data.iteritems():
            row+=1
            worksheet.write(row, col, partner.name, color)
            custom_discount_rate = 0
            price_tax = 0
            price_total = 0
            for order in orders:
                for line in order.order_line:
                    if not self.category_id or (self.category_id and self.category_id.id ==line.product_id.categ_id.id):
                        if not self.movement or (self.movement and self.movement ==line.product_id.movement):
                            row+=1
                            date_order = datetime.strptime(line.order_id.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                            worksheet.write(row, col, date_order)
                            worksheet.write(row, col+1, line.order_id.name)
                            worksheet.write(row, col+2, line.product_id.default_code)
                            worksheet.write(row, col+3, line.product_id.name)
                            worksheet.write(row, col+4, line.product_uom_qty)
                            worksheet.write(row, col+5, line.price_unit)
                            worksheet.write(row, col+6, line.custom_discount_rate)
                            worksheet.write(row, col+7, line.price_tax)
                            worksheet.write(row, col+8, line.price_total)
                            custom_discount_rate+=line.custom_discount_rate
                            price_tax+=line.price_tax
                            price_total+=line.price_total
            row+=1
            worksheet.write(row, col, "Sub Total", total_format)
            worksheet.write(row, col+6, custom_discount_rate, total_format)
            worksheet.write(row, col+7, price_tax, total_format)
            worksheet.write(row, col+8, price_total, total_format)
            amount_discount+=custom_discount_rate
            amount_tax+=price_tax
            amount_total+=price_total
            row+=1
        worksheet.write(row, col, "Grand Total", total_format)
        worksheet.write(row, col+6, amount_discount, total_format)
        worksheet.write(row, col+7, amount_tax, total_format)
        worksheet.write(row, col+8, amount_total, total_format)
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': self.report +'.xls', 'datas_fname': self.report +'.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
        }

    @api.multi
    def print_so_per_itemreport(self, output, worksheet, workbook, title_format, total_format, bold_format, row, col):
        worksheet.write(row, col, unicode('Date', "utf-8"), title_format)
        worksheet.write(row, col+1, unicode('SOD No', "utf-8"), title_format)
        worksheet.write(row, col+2, unicode('Customer', "utf-8"), title_format)
        worksheet.write(row, col+3, unicode('Qty', "utf-8"), title_format)
        worksheet.write(row, col+4, unicode('Price', "utf-8"), title_format)
        worksheet.write(row, col+5, unicode('Disc', "utf-8"), title_format)
        worksheet.write(row, col+6, unicode('Tax', "utf-8"), title_format)
        worksheet.write(row, col+7, unicode('Total', "utf-8"), title_format)
        orders = self.get_orders()
        amount_discount = 0
        amount_tax = 0
        amount_total = 0
        amount_untaxed = 0
        data = {}
        record_list = []
        for order in orders:
            for line in order.order_line:
                if data.get(line.product_id):
                    data[line.product_id].append(order)
                else:
                    data[line.product_id] = [order]
        color = workbook.add_format({'color': '#0B0BA9','bold': 1})
        for product,orders in data.iteritems():
            if not self.category_id or (self.category_id and self.category_id.id ==product.categ_id.id):
                row+=1
                worksheet.write(row, col, product.name, color)
                custom_discount_rate = 0
                price_tax = 0
                price_total = 0
                for order in orders:
                    for line in order.order_line:
                        if line.product_id.id == product.id:
                            row+=1
                            date_order = datetime.strptime(line.order_id.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                            worksheet.write(row, col, date_order)
                            worksheet.write(row, col+1, line.order_id.name)
                            worksheet.write(row, col+2, line.order_id.partner_id.name)
                            worksheet.write(row, col+3, line.product_uom_qty)
                            worksheet.write(row, col+4, line.price_unit)
                            worksheet.write(row, col+5, line.custom_discount_rate)
                            worksheet.write(row, col+6, line.price_tax)
                            worksheet.write(row, col+7, line.price_total)
                            custom_discount_rate+=line.custom_discount_rate
                            price_tax+=line.price_tax
                            price_total+=line.price_total
                row+=1
                worksheet.write(row, col, "Sub Total", total_format)
                worksheet.write(row, col+5, custom_discount_rate, total_format)
                worksheet.write(row, col+6, price_tax, total_format)
                worksheet.write(row, col+7, price_total, total_format)
                amount_discount+=custom_discount_rate
                amount_tax+=price_tax
                amount_total+=price_total
                row+=1
        worksheet.write(row, col, "Grand Total", total_format)
        worksheet.write(row, col+5, amount_discount, total_format)
        worksheet.write(row, col+6, amount_tax, total_format)
        worksheet.write(row, col+7, amount_total, total_format)
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': self.report +'.xls', 'datas_fname': self.report +'.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
        }

    @api.multi
    def print_so_realizationreport(self, output, worksheet, workbook, title_format, total_format, bold_format, row, col):
        worksheet.write(row, col, unicode('SOD No', "utf-8"), title_format)
        worksheet.write(row, col+1, unicode('Date', "utf-8"), title_format)
        worksheet.write(row, col+2, unicode('Last DO', "utf-8"), title_format)
        worksheet.write(row, col+3, unicode('Item Code', "utf-8"), title_format)
        worksheet.write(row, col+4, unicode('Item Name', "utf-8"), title_format)
        worksheet.write(row, col+5, unicode('Ordered', "utf-8"), title_format)
        worksheet.write(row, col+6, unicode('Delivered', "utf-8"), title_format)
        orders = self.get_orders()
        amount_discount = 0
        amount_tax = 0
        amount_total = 0
        amount_untaxed = 0
        data = {}
        orders = orders.filtered(lambda a: a.picking_ids)
        for order in orders:
            if data.get(order.partner_id):
                data[order.partner_id].append(order)
            else:
                data[order.partner_id] = [order]
        color = workbook.add_format({'color': '#0B0BA9','bold': 1})
        for partner,orders in data.iteritems():
            row+=1
            worksheet.write(row, col, partner.name, color)
            custom_discount_rate = 0
            product_qty = 0
            qty_done = 0
            for order in orders:
                for picking in order.picking_ids:
                    for line in picking.pack_operation_product_ids:
                        if not self.category_id or (self.category_id and self.category_id.id == line.product_id.categ_id.id):
                            row+=1
                            date_order = datetime.strptime(order.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                            worksheet.write(row, col, order.name)
                            worksheet.write(row, col+1, date_order)
                            worksheet.write(row, col+2, datetime.strptime(picking.min_date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y'))
                            worksheet.write(row, col+3, line.product_id.default_code)
                            worksheet.write(row, col+4, line.product_id.name)
                            worksheet.write(row, col+5, line.product_qty)
                            worksheet.write(row, col+6, line.qty_done)
                            product_qty+=line.product_qty
                            qty_done+=line.qty_done
            row+=1
            worksheet.write(row, col+5, product_qty, total_format)
            worksheet.write(row, col+6, qty_done, total_format)
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': self.report +'.xls', 'datas_fname': self.report +'.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
        }

    @api.multi
    def get_orders(self):
        data = {}
        domain = [('date_order','>=',self.from_date),('date_order','<=',self.to_date)]
        if self.partner_id:
            domain.append(('partner_id','=',self.partner_id.id))
        return self.env['sale.order'].search(domain)

    @api.multi
    def get_order_per_customer(self):
        data = {}
        domain = [('date_order','>=',self.from_date),('date_order','<=',self.to_date)]
        if self.partner_id:
            domain.append(('partner_id','=',self.partner_id.id))
        orders = self.env['sale.order'].search(domain)
        data = {}
        result = {}
        for order in orders:
            if data.get(order.partner_id):
                data[order.partner_id].append(order)
            else:
                data[order.partner_id] = [order]
        for partner,orders in data.iteritems():
            result[partner.name] = {}
            custom_discount_rate = 0
            price_tax = 0
            price_total = 0
            records = []
            for order in orders:
                for line in order.order_line:
                    vals={}
                    if not self.category_id or (self.category_id and self.category_id.id ==line.product_id.categ_id.id):
                        if not self.movement or (self.movement and self.movement ==line.product_id.movement):
                            date_order = datetime.strptime(line.order_id.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                            vals['date_order'] = date_order
                            vals['so_name'] = line.order_id.name
                            vals['default_code'] = line.product_id.default_code
                            vals['product_name'] = line.product_id.name
                            vals['qty'] = line.product_uom_qty
                            vals['price_unit'] = line.price_unit
                            vals['discount'] = line.custom_discount_rate
                            vals['tax'] = line.price_tax
                            vals['total'] = line.price_total
                            vals['company_id'] = order.company_id
                            records.append(vals)
            result[partner.name] = records
        return result
    
    @api.multi
    def get_order_per_item(self):
        data = {}
        domain = [('date_order','>=',self.from_date),('date_order','<=',self.to_date)]
        if self.partner_id:
            domain.append(('partner_id','=',self.partner_id.id))
        orders = self.env['sale.order'].search(domain)
        data = {}
        result = {}
        for order in orders:
            for line in order.order_line:
                if data.get(line.product_id):
                    data[line.product_id].append(order)
                else:
                    data[line.product_id] = [order]
        for product,orders in data.iteritems():
            if not self.category_id or (self.category_id and self.category_id.id ==product.categ_id.id):
                custom_discount_rate = 0
                price_tax = 0
                price_total = 0
                records = []
                for order in orders:
                    for line in order.order_line:
                        vals={}
                        if line.product_id.id == product.id:
                            date_order = datetime.strptime(line.order_id.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                            vals['date_order'] = date_order
                            vals['so_name'] = line.order_id.name
                            vals['customer'] = line.order_id.partner_id.name
                            vals['qty'] = line.product_uom_qty
                            vals['price'] = line.price_unit
                            vals['discount'] = line.custom_discount_rate
                            vals['tax'] = line.price_tax
                            vals['total'] = line.price_total
                            vals['company_id'] = order.company_id
                            vals['currency_name'] = order.pricelist_id.currency_id.name
                            records.append(vals)
            result[product.name] = records
        return result

    @api.multi
    def get_order_customer_realization(self):
        data = {}
        domain = [('date_order','>=',self.from_date),('date_order','<=',self.to_date)]
        if self.partner_id:
            domain.append(('partner_id','=',self.partner_id.id))
        orders = self.env['sale.order'].search(domain)
        orders = orders.filtered(lambda a: a.picking_ids)
        data = {}
        result = {}
        for order in orders:
            if data.get(order.partner_id):
                data[order.partner_id].append(order)
            else:
                data[order.partner_id] = [order]
        for partner,orders in data.iteritems():
            custom_discount_rate = 0
            product_qty = 0
            qty_done = 0
            records = []
            for order in orders:
                for picking in order.picking_ids:
                    for line in picking.pack_operation_product_ids:
                        vals={}
                        if not self.category_id or (self.category_id and self.category_id.id == line.product_id.categ_id.id):
                            date_order = datetime.strptime(order.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                            vals['so_name'] = order.name
                            vals['date'] = date_order
                            vals['last_do'] =  datetime.strptime(picking.min_date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                            vals['default_code'] = line.product_id.default_code
                            vals['product'] = line.product_id.name
                            vals['qty'] = line.product_qty
                            vals['qty_done'] = line.qty_done
                            records.append(vals)
            result[partner.name] = records
        return result