# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import misc
# import xlsxwriter
import base64
import xlwt
from xlwt import Workbook, easyxf
from StringIO import StringIO
from odoo import tools, api, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class vendor_bill_report(models.TransientModel):
    _name = 'vendor.bill.report'

    customer_id = fields.Many2one('account.invoice',string="Vendor Name")

    @api.multi
    def generate_excel(self):
        filename = 'Vendor Bill Report.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        worksheet = workbook.add_sheet('Vendor Bill Report')
        style = xlwt.easyxf('font:height 200, bold True, name Arial;align: horiz center;')
        style_main_header = xlwt.easyxf('font: height 250, bold True, color black;\
                                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                                              left medium, right medium, top medium, bottom medium;\
                                     pattern: pattern solid, fore_color white; align: horiz center;')

        worksheet.write_merge(0, 0, 0, 26, 'Vendor Bill Report', style_main_header)
        worksheet.write(1, 0, 'TGC INVOICE No', style)
        worksheet.write(1, 1, 'DD Invoice No.', style)
        worksheet.write(1, 2, 'Buyer Name', style)
        worksheet.write(1, 3, 'P/O. No.', style)
        worksheet.write(1, 4, 'Style No', style)
        worksheet.write(1, 5, 'Margin Required %', style)
        worksheet.write(1, 6, 'TEO’S Margin \n Required Based \n Price', style)
        worksheet.write(1, 7, 'Documentation \n surcharge', style)
        worksheet.write(1, 8, 'Teo’s margin \n required \n based price \n aft surcharge', style)
        worksheet.write(1, 9, 'Buyer’s price', style)
        worksheet.write(1, 10, 'Indigo’s \n margin based \n nt fob', style)
        worksheet.write(1, 11, 'DD’s price \n from margin \n required', style)
        worksheet.write(1, 12, 'DD’s invoice \n price', style)
        worksheet.write(1, 13, 'Profit from \n DD based on \n margin \n required', style)
        worksheet.write(1, 14, 'Profit from \n buyer for \n price diff ', style)
        worksheet.write(1, 15, 'Quantity', style)
        worksheet.write(1, 16, 'Profit from \n DD based \n on margin required', style)
        worksheet.write(1, 17, 'Profit from \n buyer from \n price diff', style)
        worksheet.write(1, 18, 'Total profit', style)
        worksheet.write(1, 19, 'Over/under \n charged by dd', style)
        worksheet.write(1, 20, 'To issue d/n/(c/n) to dd', style)
        worksheet.write(1, 21, 'Season', style)
        worksheet.write(1, 22, 'Invoice Date', style)
        worksheet.write(1, 23, 'Commission Payable To', style)
        worksheet.write(1, 24, 'Commission Payable %', style)
        worksheet.write(1, 25, 'Commission payable', style)
        worksheet.write(1, 26, 'JV No. For commission', style)

        row = 2
        worksheet.row(0).height = 500
        worksheet.row(1).height = 1000
        # worksheet.row(row).height=400
        # worksheet.row(row+1).height=400
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 10000
        worksheet.col(2).width = 10000
        worksheet.col(3).width = 10000
        worksheet.col(4).width = 10000
        worksheet.col(5).width = 10000
        worksheet.col(6).width = 10000
        worksheet.col(7).width = 10000
        worksheet.col(8).width = 10000
        worksheet.col(9).width = 10000
        worksheet.col(10).width = 10000
        worksheet.col(11).width = 10000
        worksheet.col(12).width = 10000
        worksheet.col(13).width = 10000
        worksheet.col(14).width = 10000
        worksheet.col(15).width = 10000
        worksheet.col(16).width = 10000
        worksheet.col(17).width = 10000
        worksheet.col(18).width = 10000
        worksheet.col(19).width = 10000
        worksheet.col(20).width = 10000
        worksheet.col(21).width = 10000
        worksheet.col(22).width = 10000
        worksheet.col(23).width = 10000
        worksheet.col(24).width = 10000
        worksheet.col(25).width = 10000
        worksheet.col(26).width = 10000

        vendor = self.customer_id

        if vendor.invoice_line_ids:
            for invoice_line in vendor.invoice_line_ids:
                column = 0
                # worksheet.write(row, column, vendor.partner_id.id and vendor.partner_id.name)
                if vendor.c_number:
                    worksheet.write(row, column, vendor.c_number)
                if vendor.dd_invoice_no:
                    worksheet.write(row, column + 1, vendor.dd_invoice_no)
                if vendor.partner_id.name:
                    worksheet.write(row, column + 2, vendor.partner_id.name)
                if invoice_line.po_no:
                    worksheet.write(row, column + 3, invoice_line.po_no)
                if invoice_line.style_no:
                    worksheet.write(row, column + 4, invoice_line.style_no)
                if invoice_line.margin_required:
                    worksheet.write(row, column + 5, invoice_line.margin_required)

                # g. TEO’S Margin Required Based Price
                worksheet.write(row, column + 6, '')
                # h. Documentation surcharge
                worksheet.write(row, column + 7, '')
                # i. Teo’s margin required based price aft surcharge
                worksheet.write(row, column + 8, '')

                if vendor.amount_total:
                    worksheet.write(row, column + 9, vendor.amount_total)

                #k. Indigo’s margin based nt fob
                worksheet.write(row, column + 10, '')

                #l. DD’s price from margin required
                worksheet.write(row, column + 11, '')

                if invoice_line.price_subtotal:
                    worksheet.write(row, column + 12, invoice_line.price_subtotal)

                #n. Profit from DD based on margin required
                worksheet.write(row, column + 13, '')

                #o. Profit from buyer for price diff
                worksheet.write(row, column + 14, '')

                if invoice_line.quantity:
                    worksheet.write(row, column + 15, invoice_line.quantity)

                #q. Profit from DD based on margin required
                worksheet.write(row, column + 16, '')

                #r. Profit from buyer from price diff
                worksheet.write(row, column + 17, '')

                #s. Total profit
                worksheet.write(row, column + 18, '')

                #t. Over/under charged by dd
                worksheet.write(row, column + 19, '')

                #u. To issue d/n/(c/n) to dd
                worksheet.write(row, column + 20, '')

                if vendor.season:
                    worksheet.write(row, column + 21, vendor.season)

                if vendor.invoice_date:
                    worksheet.write(row, column + 22, vendor.invoice_date)

                if vendor.commission_payable_to:
                    worksheet.write(row, column + 23, vendor.invoice_date)

                if invoice_line.commission_payable:
                    worksheet.write(row, column + 24, invoice_line.commission_payable)

                #z. Commission payable
                    worksheet.write(row, column + 25, '')

                #r commission
                    worksheet.write(row, column + 26, '')
                row += 1
        else:
            raise ValidationError(_('Please select Vendor First'))

        fp = StringIO()
        workbook.save(fp)
        export_id = self.env['excel.extended'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'excel.extended',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }