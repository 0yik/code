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
import StringIO
import xlsxwriter
import csv
import os.path


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def download_txt(self):
        customer_ids = self._context.get('active_ids',[])
        if customer_ids:
            content = str('Cust. Code') + '  ' + str('Cust. Name') + '  ' +\
                        str('Mailing Address Name') + '   ' + str('Mailing Address Street/Box 1') + '  ' +\
                        str('Mailing Address Street/Box 2') + '   ' + str('Mailing address Zip/City 1') + '  ' +\
                        str('Mailing address Zip/City 2') + '  ' + str('Delivery address Name') + '  ' +\
                        str('Delivery address Street/box 1') + '  ' + str('Delivery address Street/box 2') + '  ' +\
                        str('Delivery address Zip/City 1') + '  ' + str('Delivery address Zip/City 2') + '  ' +\
                        str('Language') + '  ' + str('Currency') + '  ' +\
                        str('Customer Group') + '  ' + str('VAT Code') + '  ' +\
                        str('VAT number') + '  ' + str('Country Code') + '  ' +\
                        str('Phone') + '  ' + str('Fax') + '  ' +\
                        str('E-mail') + '  ' + str('Ref. Name') + '  ' +\
                        str('Ref Phone') + '  ' + str('Ref. Mobile Phone') + '  ' +\
                        str('Ref. E-mail') + '  ' + '\n'
            for customer in self.env['res.partner'].browse(customer_ids):
                content += str(customer.partner_code or '\t') + ' ' + str(customer.name  or '\t') + '	' + str(customer.mailing_address_name or '\t') +'   '+\
                        str(customer.street or '\t')+ '	'+str(customer.street2 or '\t')+ '  ' + str(customer.city or customer.zip or '\t') + '  ' + str(customer.city2_mailing or customer.zip2_mailing or '\t') + '  '+\
                        str(customer.delivery_address_name or '\t')+ ' '+ str(customer.street_delivery or '\t')+ '  '+str(customer.street2_delivery or '\t')+ '  '+\
                        str(customer.city_delivery or customer.zip_delivery or '\t')+ '  '+ str(customer.city2_delivery or customer.zip2_delivery or '\t')+ '  '+str(customer.lang or '\t')+ '  '+\
                        str(customer.currency_new_id and customer.currency_new_id.name or '\t')+ '	'+str(customer.customer_group_id and customer.customer_group_id.name or '\t')+ '  ' +\
                        str(customer.vat_code or '\t')+ '   ' +str(customer.vat_number or '\t')+ '   ' + str(customer.country_id and customer.country_id.code or '\t') + '    ' + \
                        str(customer.phone or '\t')+ '   ' +str(customer.fax or '\t') + '   ' +str(customer.email or '\t')+ '   ' +\
                        str(customer.ref_name or '\t')+ '   ' +str(customer.ref_phone or '\t') + '   ' +str(customer.ref_mobile or '\t')+ '   ' +str(customer.ref_email or '\t')+ '\n' 
            filename = '/opt/odoo/Customers.txt'
            f = open(filename, 'w')
            f.write(content)
            f.close()
            file_base64 = ''
            with open(filename, "r") as file:
                file_base64 = base64.b64encode(file.read())
            export_id = self.env['customer.txt.file'].create({
                                                    'txt_file': file_base64,
                                                    'file_name': filename,
                                                    })
            return {
                    'view_mode': 'form',
                    'res_id': export_id.id,
                    'res_model': 'customer.txt.file',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'context': self._context,
                    'target': 'new',
                    }


    def download_excel(self):
        customer_ids = self._context.get('active_ids',[])
        if customer_ids:
            res = self
            output =  StringIO.StringIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Sheet1')
            row = 0
            col = 0
            bold_format = workbook.add_format({'bold':  1})
            right_format = workbook.add_format({'bold':1,'align':'right'})
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter'})
            
            worksheet.write(row, col,  unicode('Cust. Code', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Cust. Name', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col,unicode('Mailing Address Name', "utf-8") , bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Mailing Address Street/Box 1', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Mailing Address Street/Box 2', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Mailing address Zip/City 1', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Mailing address Zip/City 2', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Delivery address Name', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Delivery address Street/box 1', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Delivery address Street/box 2', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Delivery address Zip/City 1', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Delivery address Zip/City 2', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Language', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Currency', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Customer Group', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('VAT Code', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('VAT Number', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Country Code', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Phone', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Fax', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Email', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Ref. Name', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Ref. Phone', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Ref. Mobile Phone', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            worksheet.write(row, col, unicode('Ref. E-mail', "utf-8"), bold_format)
            worksheet.set_column(row, col, 20)
            col += 1

            for customer in self.env['res.partner'].browse(customer_ids):
                for child in customer.child_ids:
                    row += 1
                    col = 0

                    if customer.partner_code:
                        worksheet.write(row, col,customer.partner_code or ' ')
                    col += 1
                    
                    if customer.name:
                        worksheet.write(row, col,customer.name or ' ')
                    col += 1

                    if customer.mailing_address_name:
                        worksheet.write(row, col,customer.mailing_address_name or ' ')
                    col += 1

                    if customer.street:     
                        worksheet.write(row, col,customer.street or ' ')
                    col += 1

                    if customer.street2:
                        worksheet.write(row, col,customer.street2 or ' ')
                    col += 1

                    if customer.city:
                        worksheet.write(row, col,str(customer.city or ' ')+ ' ' + str(customer.zip or '') or '')
                    col += 1

                    if customer.city2_mailing:
                        worksheet.write(row, col,str(customer.city2_mailing or ' ')+ ' ' + str(customer.zip2_mailing or '') or '')
                    col += 1

                    if customer.delivery_address_name:
                        worksheet.write(row, col,customer.delivery_address_name or ' ')
                    col += 1
                    
                    if customer.street_delivery:
                        worksheet.write(row, col,customer.street_delivery or ' ')
                    col += 1

                    if customer.street2_delivery:
                        worksheet.write(row, col,customer.street2_delivery or ' ')
                    col += 1

                    if customer.city_delivery:
                        worksheet.write(row, col,str(customer.city_delivery or ' ') +' '+str(customer.zip_delivery or '') or '')
                    col += 1

                    if customer.street2_delivery:
                        worksheet.write(row, col,str(customer.street2_delivery or ' ') +' '+ str(customer.city2_delivery or '') or '')
                    col += 1

                    if customer.lang == 'en_US':
                        worksheet.write(row, col,'EN')
                        col += 1
                    elif customer.lang:
                        worksheet.write(row, col,customer.lang or ' ')
                        col += 1
                    else:
                        col += 1

                    if customer.currency_new_id:
                        worksheet.write(row, col,customer.currency_new_id.name or ' ')
                    col += 1

                    if customer.customer_group_id:
                        worksheet.write(row, col,customer.customer_group_id.name or ' ')
                    col += 1

                    if customer.vat_code:
                        worksheet.write(row, col,customer.vat_code or ' ')
                    col += 1

                    if customer.vat_number:
                        worksheet.write(row, col,customer.vat_number or ' ')
                    col += 1

                    if customer.country_id:
                        worksheet.write(row, col,customer.country_id.code or ' ')
                    col += 1

                    if customer.phone:
                        worksheet.write(row, col,customer.phone or ' ')
                    col += 1

                    if customer.fax:
                        worksheet.write(row, col,customer.fax or ' ')
                    col += 1

                    if customer.email:
                        worksheet.write(row, col,customer.email or ' ')
                    col += 1

                    if child:
                        worksheet.write(row, col,child.name or ' ')
                    col += 1

                    if child and child.phone:
                        worksheet.write(row, col,child.phone or ' ')
                    col += 1

                    if child and child.mobile:
                        worksheet.write(row, col,child.mobile or ' ')
                    col += 1

                    if child and child.email:
                        worksheet.write(row, col,child.email or ' ')
                    col += 1


            row += 1

            workbook.close()
            output.seek(0)
            result = base64.b64encode(output.read())
            attachment_obj = self.env['ir.attachment']
            attachment_id = attachment_obj.create({'name': 'Customer Excel.xlsx', 'datas_fname': 'Customer Excel.xlsx', 'datas': result})
            download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')

            return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
                "target": "self",
            }