from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import base64
from cStringIO import StringIO
#import StringIO
#import xlsxwriter #this package is not supported form me that's a reasone in local we use  import xlwt and replace for xlsxwriter
import xlwt
import csv
import os.path
import pytz

class PurchaseReporsWizard(models.TransientModel):
    _name = "purchase.reports.wizard"

    report = fields.Selection([('po_per_supplier','Purchase Order Per Supplier'),
                               ('po_realization','Purchase Order Realization')], 
                              string="Report")
    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor')
    category_id = fields.Many2one('product.category', string="Category")
    format = fields.Selection([('pdf','PDF'),('xls','XLS')], string="Format", default='pdf')
    movement = fields.Selection([('discontinue','Discontinue'),('running','Running'),('slow','Slow')])

    @api.multi
    def print_report(self):
        if self.format=='pdf':
            
            if self.report == 'po_per_supplier':
                return self.env['report'].get_action(self, 'pdp_modifier_purchase_report.report_purchaseorder_per_supplier')
            else:
                return self.env['report'].get_action(self, 'pdp_modifier_purchase_report.report_purchaseorder_realization')
        
        else:
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('sheet1') 
            row = 1
            col = 0
            bold_format = xlwt.easyxf('font: bold on;')
            po_title = xlwt.easyxf('align: vertical center, horizontal center; font: bold on;font:height 280;border: top medium, bottom medium, right medium, left medium;')
            font_size_format = xlwt.easyxf('font: bold on;')
            current_time = datetime.now()
            current_time_utc = pytz.timezone('UTC').localize(current_time, is_dst=False)
            if not self.env.user.tz:
                raise UserError(_("Pleas select Time zone in Users"))
            current_time = current_time_utc.astimezone(pytz.timezone(self.env.user.tz))
            current_time = str(current_time)[:19]
            current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %I:%M %p')
            worksheet.write(row, col, unicode('Printed : ' + str(current_time), "utf-8"), font_size_format)
            col+=4
            if self.report=='po_per_supplier':
                report_name = 'PURCHASE ORDER PER SUPPLIER'
                new_row = row + 1
                worksheet.write_merge(row, new_row, 3, 7, report_name, po_title)
                row+=2
                worksheet.write_merge(row, row, col-1, col+3, unicode('Period : ' + self.from_date + ' 00:00' + ' Upto ' + self.to_date + ' 23:59', "utf-8"),  xlwt.easyxf('align: vertical center, horizontal center; font: bold on;'))
            else:
                #report_name = 'Purchase Order Supplier Realization'
                report_name = 'LAPORAN REALISASI PO'
                new_row = row + 1
                worksheet.write_merge(row, new_row, 3, 6, report_name, po_title)
                row+=2
                worksheet.write_merge(row, row, col-1, col+2, unicode('Period : ' + self.from_date + ' 00:00' + ' Upto ' + self.to_date + ' 23:59', "utf-8"),  xlwt.easyxf('align: vertical center, horizontal center; font: bold on;'))
            
            
           
            row+=2
            col=0
            title_format = xlwt.easyxf('font: bold on;font:height 220;border: top medium;border: bottom medium; border: right medium; border: left medium;')
            total_format = xlwt.easyxf('font: bold on; border: top medium;border: bottom medium; border: right medium; border: left medium;pattern: pattern solid, fore_colour yellow;')

            if self.report=='po_per_supplier':
                return self.print_po_per_supplierreport(worksheet, workbook, title_format, total_format, bold_format, row, col)
            else:
                return self.print_po_realizationreport(worksheet, workbook, title_format, total_format, bold_format, row, col)

    @api.multi
    def print_po_per_supplierreport(self, worksheet, workbook, title_format, total_format, bold_format, row, col):
        worksheet.write(row, col, unicode('Date', "utf-8"), title_format)
        col+=1
        worksheet.write(row, col, unicode('POD No', "utf-8"), title_format)
        col+=1
        worksheet.write(row, col, unicode('Item Code', "utf-8"), title_format)
        col+=1
        worksheet.write(row, col, unicode('Item Name', "utf-8"), title_format)
        worksheet.col(col).width = 256 * 28 #28 characters wide (-ish)
        col+=1
        worksheet.write(row, col, unicode('Cur', "utf-8"), title_format)
        col+=1
        worksheet.write(row, col, unicode('Qty', "utf-8"), title_format)
        col+=1
        worksheet.write(row, col, unicode('Price', "utf-8"), title_format)
        col+=1
        worksheet.write(row, col, unicode('Disc', "utf-8"), title_format)
        col+=1
        worksheet.write(row, col, unicode('Tax', "utf-8"), title_format)
        col+=1
        worksheet.write(row, col, unicode('Total', "utf-8"), title_format)
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
        color = xlwt.easyxf('font: color blue; font: bold on;border: bottom medium;border: top medium;border: right medium; border: left medium;')
        for partner,orders in data.iteritems():
            row+=1
            col=0
            worksheet.write_merge(row, row, 0, 9, partner.name, color)
            supplier_discount_rate = 0
            price_tax = 0
            price_total = 0
            for order in orders:
                for line in order.order_line:
                    if not self.category_id or (self.category_id and self.category_id.id ==line.product_id.categ_id.id):
                        if not self.movement or (self.movement and self.movement ==line.product_id.movement):
                            row+=1
                            col=0
                            date_order = datetime.strptime(line.order_id.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                            worksheet.write(row, col, date_order)
                            col+=1
                            worksheet.write(row, col, line.order_id.name)
                            col+=1
                            worksheet.write(row, col, line.product_id.default_code)
                            col+=1
                            worksheet.write(row, col, line.product_id.name)
                            col+=1
                            worksheet.write(row, col, order.pricelist_id.currency_id.name)
                            col+=1
                            worksheet.write(row, col, line.product_qty)
                            col+=1
                            worksheet.write(row, col, line.price_unit)
                            col+=1
                            #if line.discount_rate:
                            worksheet.write(row, col, line.discount_rate)
                            col+=1
                            #if line.price_tax:
                            worksheet.write(row, col, line.price_tax)
                            col+=1
                            worksheet.write(row, col, line.price_total)
                            col+=1
                            supplier_discount_rate+=line.discount_rate
                            price_tax+=line.price_tax
                            price_total+=line.price_total
            row+=1
            col=0
            worksheet.write_merge(row, row, col ,col+6, "Sub Total",xlwt.easyxf('font: bold on; border: top medium;border: bottom medium; border: right medium; border: left medium;'))
            worksheet.write(row, col+7, supplier_discount_rate, total_format)
            worksheet.write(row, col+8, price_tax, total_format)
            worksheet.write(row, col+9, price_total, total_format)
            amount_discount+=supplier_discount_rate
            amount_tax+=price_tax
            amount_total+=price_total
            row+=2
        col=0
        worksheet.write_merge(row-1, row-1, col ,col+6, "Grand Total",xlwt.easyxf('font: bold on; border: top medium;border: bottom medium; border: right medium; border: left medium;'))
        worksheet.write(row-1, col+7, amount_discount, total_format)
        worksheet.write(row-1, col+8, amount_tax, total_format)
        worksheet.write(row-1, col+9, amount_total, total_format)
        fp = StringIO()
        workbook.save(fp)
        
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': self.report +'.xls', 'datas_fname': self.report +'.xlsx', 'datas': base64.encodestring(fp.getvalue())})
        fp.close()
        
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
        }

    
    @api.multi
    def print_po_realizationreport(self, worksheet, workbook, title_format, total_format, bold_format, row, col):
        
        orders = self.get_orders()
        amount_discount = 0
        amount_tax = 0
        amount_total = 0
        amount_untaxed = 0
        data = {}
        orders = orders.filtered(lambda a: a.picking_ids)
        for order in orders:
            #partner wise
            '''if data.get(order.partner_id):
                data[order.partner_id].append(order)
            else:
                data[order.partner_id] = [order]'''
            #internal categorywise    
            for line in order.order_line:
                if data.get(line.product_id.categ_id):
                    if order not in data[line.product_id.categ_id]: 
                        data[line.product_id.categ_id].append(order)
                else:
                    data[line.product_id.categ_id] = [order]
                    
        color = xlwt.easyxf('font: color blue; font: bold on;border: bottom medium;border: top medium;border: right medium; border: left medium;')
        for partner,orders in data.iteritems():
            row+=1
            col=0
            worksheet.write_merge(row, row, 0, 7, partner.name, color)
            row+=1
            col=0
            worksheet.write(row, col, unicode('POD No', "utf-8"), title_format)
            col+=1
            worksheet.write(row, col, unicode('Ref No', "utf-8"), title_format)
            col+=1
            worksheet.write(row, col, unicode('Date', "utf-8"), title_format)
            col+=1
            worksheet.write(row, col, unicode('Last Rcv', "utf-8"), title_format)
            col+=1
            worksheet.write(row, col, unicode('Item Code', "utf-8"), title_format)
            col+=1
            worksheet.write(row, col, unicode('Item Name', "utf-8"), title_format)
            worksheet.col(col).width = 256 * 28 #28 characters wide (-ish)
            col+=1
            worksheet.write(row, col, unicode('Ordered', "utf-8"), title_format)
            col+=1
            worksheet.write(row, col, unicode('Received', "utf-8"), title_format)
            #worksheet.write(row, col, partner.name, color)
            custom_discount_rate = 0
            product_qty = 0
            qty_done = 0
            for order in orders:
                for picking in order.picking_ids:
                    for line in picking.pack_operation_product_ids:
                        if not self.category_id or (self.category_id and self.category_id.id == line.product_id.categ_id.id):
                            row+=1
                            col=0
                            date_order = datetime.strptime(order.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                            worksheet.write(row, col, order.name)
                            col+=1
                            if order.partner_ref:
                                worksheet.write(row, col, order.partner_ref)
                            col+=1
                            worksheet.write(row, col, date_order)
                            col+=1
                            worksheet.write(row, col, datetime.strptime(order.receive_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
                            col+=1
                            worksheet.write(row, col, line.product_id.default_code)
                            col+=1
                            worksheet.write(row, col, line.product_id.name)
                            col+=1
                            if order.received_status == 'Done':
                                worksheet.write(row, col, line.product_qty)
                            col+=1
                            if order.received_status == 'Done' and line.qty_done:
                                worksheet.write(row, col, line.qty_done)
                            col+=1
                            if order.received_status == 'Done':
                                product_qty+=line.product_qty
                                qty_done+=line.qty_done
            row+=1
            col=0
            worksheet.write_merge(row, row, col ,col+5, "Total",xlwt.easyxf('font: bold on; border: top medium;border: bottom medium; border: right medium; border: left medium;'))
            worksheet.write(row, col+6, product_qty, total_format)
            worksheet.write(row, col+7, qty_done, total_format)
            row+=2
        fp = StringIO()
        workbook.save(fp)
        
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': self.report +'.xls', 'datas_fname': self.report +'.xlsx', 'datas': base64.encodestring(fp.getvalue())})
        fp.close()
        
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
        return self.env['purchase.order'].search(domain)

    @api.multi
    def get_order_per_customer(self):
        data = {}
        domain = [('date_order','>=',self.from_date),('date_order','<=',self.to_date)]
        if self.partner_id:
            domain.append(('partner_id','=',self.partner_id.id))
        orders = self.env['purchase.order'].search(domain)
        data = {}
        result = {}
        for order in orders:
            if data.get(order.partner_id):
                data[order.partner_id].append(order)
            else:
                data[order.partner_id] = [order]
        for partner,orders in data.iteritems():
            result[partner.name] = {}
            supplier_discount_rate = 0
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
                            vals['po_name'] = line.order_id.name
                            vals['default_code'] = line.product_id.default_code
                            vals['product_name'] = line.product_id.name
                            vals['currency'] = order.pricelist_id.currency_id.name
                            vals['qty'] = line.product_qty
                            vals['price_unit'] = line.price_unit
                            vals['discount'] = line.discount_rate
                            vals['tax'] = line.price_tax #qery please check
                            vals['total'] = line.price_total
                            vals['company_id'] = order.company_id
                            records.append(vals)
            result[partner.name] = records
        return result
    
    
    @api.multi
    def get_order_purchase_realization(self):
        data = {}
        domain = [('date_order','>=',self.from_date),('date_order','<=',self.to_date)]
        if self.partner_id:
            domain.append(('partner_id','=',self.partner_id.id))
        orders = self.env['purchase.order'].search(domain)
        orders = orders.filtered(lambda a: a.picking_ids)
        data = {}
        result = {}
        '''for order in orders:
            if data.get(order.partner_id):
                data[order.partner_id].append(order)
            else:
                data[order.partner_id] = [order]
        data = {}'''
        for order in orders:
            for line in order.order_line:
                if data.get(line.product_id.categ_id):
                    if order not in data[line.product_id.categ_id]: 
                        data[line.product_id.categ_id].append(order)
                else:
                    data[line.product_id.categ_id] = [order]  
        #for partner,orders in data.iteritems():
        for int_categ,orders in data.iteritems():
            result[int_categ.name] = {}
            #result[partner.name] = {}
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
                            vals['po_name'] = order.name
                            vals['ven_ref'] = order.partner_ref
                            vals['date'] = date_order
                            receive_date = datetime.strptime(order.receive_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                            vals['last_rcv'] = receive_date
                            vals['default_code'] = line.product_id.default_code
                            vals['product'] = line.product_id.name
                            if order.received_status == 'Done':
                                vals['qty'] = line.product_qty
                                #vals['qty'] = line.ordered_qty
                            else:
                                vals['qty'] = False
                            if order.received_status == 'Done' and line.qty_done:
                                vals['qty_received'] = line.qty_done
                            else:
                                vals['qty_received'] = False    
                                
                            records.append(vals)
            result[int_categ.name] = records
            #result[partner.name] = records
        return result
