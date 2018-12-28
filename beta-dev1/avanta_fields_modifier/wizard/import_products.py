# -*- coding: utf-8 -*-

from odoo import api, fields, models
import openpyxl
import logging
from tempfile import TemporaryFile

_logger = logging.getLogger(__name__)

class ProductImport(models.TransientModel):
    _name = 'product.import'
    _description = 'Importing Produts'

    file_to_import = fields.Binary('File to import', attachment=True)
    file_name = fields.Char("File Name", size=64, readonly=True)

    @api.multi
    def action_import_file(self):
        file = self.file_to_import.decode('base64')
        excel_fileobj = TemporaryFile('wb+')
        excel_fileobj.write(file)
        excel_fileobj.seek(0)

        workbook = openpyxl.load_workbook(excel_fileobj, data_only=True)
        sheet = workbook[workbook.get_sheet_names()[0]]
        flag =0
        for row in sheet.rows:
            product_dict = {}
            service_name = row[0].value
            internal_category = row[1].value
            product_name = row[2].value
            internal_reference = row[3].value
            sale_price = row[4].value
            cost = row[5].value
            descriptions_for_quotations = row[6].value

            if flag !=0:
                product_check = self.env['product.template'].search([('name','=',product_name)])
                service_id = self.env['product.template'].search([('name','=',service_name)])
                product_categ_id = self.env['product.category'].search([('name','=',internal_category)])
                if service_id:
                    product_dict['service_id'] = service_id.id
                    if product_categ_id:
                        product_dict['categ_id'] = product_categ_id.id
                product_dict['name'] = product_name
                product_dict['default_code'] = internal_reference
                product_dict['list_price'] = sale_price
                product_dict['standard_price'] = cost
                if descriptions_for_quotations:
                    data = [ord(x) for x in descriptions_for_quotations]
                    descriptions_for_quotations = ''.join(unichr(i) for i in data)
                    product_dict['description_sale'] = "<br/>".join(descriptions_for_quotations.split("\n"))
                else:
                    product_dict['description_sale'] = ''
                if product_check:
                    product_check.write(product_dict)
                else:
                    self.env['product.template'].create(product_dict)

            flag += 1

class IndustryTypeImport(models.TransientModel):
    _name = 'industry.type.import'
    _description = 'Industry Type Import'

    file_to_import = fields.Binary('File to import', attachment=True)
    file_name = fields.Char("File Name", size=64, readonly=True)

    @api.multi
    def action_import_file(self):
        excel_fileobj = TemporaryFile('wb+')
        file = self.file_to_import.decode('base64')
        excel_fileobj.write(file)
        excel_fileobj.seek(0)

        workbook = openpyxl.load_workbook(excel_fileobj, data_only=True)
        sheet = workbook[workbook.get_sheet_names()[0]]
        flag =0
        for row in sheet.rows:
            industry_type_dict = {}
            service_name = row[0].value

            if flag !=0:

                if service_name:
                    industry_type_check = self.env['industry.type'].search([('name','=',service_name)])
                    industry_type_dict['name'] = service_name
                    if industry_type_check:
                        _logger.info("Industry type %s already exist", industry_type_check.name)
                    else:
                        if industry_type_dict:
                            self.env['industry.type'].create(industry_type_dict)
            flag += 1