# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp

import base64
import unicodedata
import StringIO
import xlsxwriter
import csv
import os.path

class ProductProduct(models.Model):
    _inherit = 'product.product'
    def download_txt(self):
        product_ids = self._context.get('active_ids',[])
        if product_ids:
            content =   str('Part Number') + '  ' + str('Name') + '  ' +\
                        str('Part Type') + '   ' + str('Unit') + '  ' +\
                        str('Alternate Unit') + '   ' + str('Part Code') + '  ' +\
                        str('Product Group') + '  ' + str('Product Category') + '  ' +\
                        str('Drawing No.') + '  ' + str('Revision') + '  ' +\
                        str('Add Name 1') + '  ' + str('Add Name 2') + '  ' +\
                        str('Add Name 3') + '  ' + str('Add Name 4') + '  ' +\
                        str('Customer Code') + '  ' + str('Customer Price') + '  ' +\
                        str('Customer Partno') + '  ' + '\n'
            for part_number_obj in self.env['product.product'].browse(product_ids):
                if part_number_obj.part_num_ids:
                    for product in part_number_obj.part_num_ids:
                        print ":::::::::::::::",product.partner_id.partner_code ,type(product.partner_id.partner_code), type(str(product.partner_id.partner_code))
                        content +=  unicodedata.normalize('NFKD', product.name or unicode(unicode('\t'))).encode('ascii', 'ignore') + '  ' + unicodedata.normalize('NFKD', product.product_id.name or unicode('\t')).encode('ascii', 'ignore') + '  ' + unicodedata.normalize('NFKD', product.part_type_id and product.part_type_id.name or unicode('\t')).encode('ascii', 'ignore') + '   ' +\
                                    unicodedata.normalize('NFKD', product.uom_id and product.uom_id.name or unicode('\t')).encode('ascii', 'ignore') + '   ' + unicodedata.normalize('NFKD', product.uom_id and product.uom_id.name or unicode('\t')).encode('ascii', 'ignore') + '   '+ \
                                    unicodedata.normalize('NFKD', product.part_code and product.part_code.name or unicode('\t')).encode('ascii', 'ignore') + '   ' + unicodedata.normalize('NFKD', product.product_group and product.product_group.name or unicode('\t')).encode('ascii', 'ignore') + '    ' + \
                                    unicodedata.normalize('NFKD', product.product_id.product_tmpl_id.name or unicode('\t')).encode('ascii', 'ignore') + '   ' + unicodedata.normalize('NFKD', product.drawing_number or unicode('\t')).encode('ascii', 'ignore') + '   ' + unicodedata.normalize('NFKD', product.revision or unicode('\t')).encode('ascii', 'ignore') + '    ' + \
                                    unicodedata.normalize('NFKD', product.add_name_1 or unicode('\t')).encode('ascii', 'ignore') + '   ' + unicodedata.normalize('NFKD', product.add_name_2 or unicode('\t')).encode('ascii', 'ignore') + '   ' + \
                                    unicodedata.normalize('NFKD', product.add_name_3 or unicode('\t')).encode('ascii', 'ignore') + '   ' + unicodedata.normalize('NFKD', product.add_name_4 or unicode('\t')).encode('ascii', 'ignore') + '   ' + \
                                    product.partner_id.partner_code or '\t' + '   ' + str(product.lst_price or 0 )+ '   ' + \
                                    product.customer_part_no or '\t'  + '   ' + '\n'
            filename = '/opt/odoo/Products.txt'
            f = open(filename, 'w')
            f.write(content)
            f.close()
            file_base64 = ''
            with open(filename, "r") as file:
                file_base64 = base64.b64encode(file.read())
            export_id = self.env['product.txt.file'].create({
                                                    'txt_file': file_base64,
                                                    'file_name': filename,
                                                    })
            return {
                    'view_mode': 'form,tree',
                    'res_id': export_id.id,
                    'res_model': 'product.txt.file',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'context': self._context,
                    'target': 'new',
                    }


    def download_excel(self):
        product_ids = self._context.get('active_ids',[])
        if product_ids:
            res = self
            output =  StringIO.StringIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Sheet1')
            row = 0
            col = 0
            bold_format = workbook.add_format({'bold':  1})
            right_format = workbook.add_format({'bold':1,'align':'right'})
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter'})
            
            worksheet.write(row, col,  unicode('Part Number', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Product Variant Name', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col,unicode('Part Type', "utf-8") , bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Unit', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Alternate Unit', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Part Code', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Product Group', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Product Family', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Drawing Number', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Revision', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Add Name 1', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Add Name 2', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Add Name 3', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Add Name 4', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Customer Code', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Customer Price', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Customer Part No', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            for product in product_ids:
                part_number_obj = self.env['product.product'].browse(product)
                if part_number_obj.part_num_ids:
                    for product_obj in part_number_obj.part_num_ids:
                        row += 1
                        col = 0

                        worksheet.write(row, col,product_obj.name or '')
                        col += 1
                        
                        worksheet.write(row, col,product_obj.product_id.name or '')
                        col += 1

                        worksheet.write(row, col,product_obj.part_type_id.name or '')
                        col += 1

                        worksheet.write(row, col,product_obj.uom_id.name or '')
                        col += 1

                        worksheet.write(row, col,product_obj.uom_id.name or '')
                        col += 1

                        worksheet.write(row, col,product_obj.part_code.name or '')
                        col += 1

                        worksheet.write(row, col,product_obj.product_group.name or '')
                        col += 1

                        worksheet.write(row, col,product_obj.product_id.product_tmpl_id.name or '')
                        col += 1
                        
                        worksheet.write(row, col,product_obj.drawing_number or '')
                        col += 1

                        worksheet.write(row, col,product_obj.revision or '')
                        col += 1

                        worksheet.write(row, col,product_obj.add_name_1 or '')
                        col += 1

                        worksheet.write(row, col,product_obj.add_name_2 or '')
                        col += 1

                        worksheet.write(row, col,product_obj.add_name_3 or '')
                        col += 1

                        worksheet.write(row, col,product_obj.add_name_4 or '')
                        col += 1

                        worksheet.write(row, col,product_obj.partner_id.partner_code or '')
                        col += 1

                        if product_obj.lst_price:
                            worksheet.write(row, col,format((product_obj.lst_price or 0), '.2f'))
                        col += 1

                        worksheet.write(row, col,product_obj.customer_part_no or '')
                        col += 1

            row += 2
            row += 1

            workbook.close()
            output.seek(0)
            result = base64.b64encode(output.read())
            attachment_obj = self.env['ir.attachment']
            attachment_id = attachment_obj.create({'name': 'Product Excel.xlsx', 'datas_fname': 'Product Excel.xlsx', 'datas': result})
            download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')

            return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
                "target": "self",
            }