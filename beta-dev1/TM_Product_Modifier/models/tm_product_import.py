from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import tempfile
from xlrd import open_workbook
from odoo import tools
from datetime import datetime

class ImportWizard(models.TransientModel):
    _name = 'wizard.product.product.import'

    file = fields.Binary('File Product Import', filters='*.xls')

    @api.multi
    def import_products(self):
        if not self.file:
            return {}
        temp_path = tempfile.gettempdir()
        for upload_rec in self:
            csv_data = base64.decodestring(upload_rec.file)
            fp=open(temp_path+'/xsl_file.xls', 'wb+')
            fp.write(csv_data)
            fp.close()
            wb = open_workbook(temp_path+'/xsl_file.xls')
            for sheet in wb.sheets():
                try:
                    index_ic = sheet.row_values(0).index('Internal Category')
                    index_brand = sheet.row_values(0).index('Brand')
                    index_category = sheet.row_values(0).index('Category')
                    index_sub1 = sheet.row_values(0).index('Sub I')
                    index_sub2 = sheet.row_values(0).index('Sub II')
                    index_attribute_id = sheet.row_values(0).index('attribute_id')
                    index_attribute_value_ids = sheet.row_values(0).index('attribute_value_ids')
                except ValueError as e:
                    raise ValidationError(e.message)
                for rownum in range(1,sheet.nrows):
                    internal_category = str(sheet.row_values(rownum)[index_ic])
                    brand = str(sheet.row_values(rownum)[index_brand])
                    category = str(sheet.row_values(rownum)[index_category])
                    sub1 = str(sheet.row_values(rownum)[index_sub1])
                    sub2 = str(sheet.row_values(rownum)[index_sub2])
                    # category
                    if internal_category:
                        intenal_category_id = self.env['product.category'].search([('name','=',internal_category)])
                        if not intenal_category_id:
                            intenal_category_id = self.env['product.category'].create({'name':internal_category})
                    # brand
                    if brand:
                        brand_id = self.env['product.brand'].search([('name', '=', brand)])
                        if not brand_id:
                            brand_id = self.env['product.brand'].create({'name': brand})
                    # category
                    if category:
                        category_id = self.env['category.main'].search([('name','=', category)])
                        if not category_id:
                            category_id = self.env['category.main'].create({'name': category})
                    # sub1
                    if sub1:
                        sub1_id = self.env['category.subfirst'].search([('name','=',sub1)])
                        if not sub1_id:
                            sub1_id = self.env['category.subfirst'].create({'name': sub1})
                    # sub2
                    if sub2:
                        sub2_id = self.env['category.subsecond'].search([('name','=',sub2)])
                        if not sub2_id:
                            sub2_id = self.env['category.subsecond'].create({'name': sub2})

                    index = 0
                    attribute_values = str(sheet.row_values(rownum)[index_attribute_value_ids]).split(',')
                    for attribute_value in attribute_values:
                        if attribute_value:
                            attribute_value_id = self.env['product.attribute.value'].search([('name','=',attribute_value)])
                            if not attribute_value_id:
                                attribute = str(sheet.row_values(rownum)[index_attribute_id]).split(',')[index]
                                attribute_id = self.env['product.attribute'].search([('name', '=', attribute)])
                                if not attribute_id:
                                    attribute_id = self.env['product.attribute'].create({'name':attribute})
                                attribute_value_id = self.env['product.attribute.value'].create({'name':attribute_value,'attribute_id':attribute_id.id})
                        index +=1
        return {}