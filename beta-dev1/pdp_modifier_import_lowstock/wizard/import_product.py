# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError, Warning
import StringIO
import base64
import xlrd
import urllib2
import csv
import codecs



class import_product_with_qty_csv_xls_file(models.TransientModel):
    _name = 'import.product.with.qty.csv.xls.file'

    file_type = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string="Select Model", default="csv")
    import_file = fields.Binary('Upload File', required=True)
    file_name = fields.Char('File Name', size=256)
    
    def import_product_with_qty(self):
        active_id = self._context.get('active_id')
        current_record = self.env['low.stock.notification'].browse(active_id)
        product_obj = self.env['product.product']
        if not self.import_file:
            raise UserError(_('Please Choose The File!'))
        file_name = self.file_name
        fname = str(file_name.split('.')[-1])
        if self.file_type == 'xls':
            if fname != 'xls' and fname != 'xlsx':
                raise UserError(_('Please choose the file with .xls/.xlsx extension and proper format!'))
                
            val = base64.decodestring(self.import_file)    
            #StringIO use Read and write strings as files
            fp = StringIO.StringIO()
            fp.write(val)
            wb = xlrd.open_workbook(file_contents=fp.getvalue())
            wb.sheet_names()
            sheet_name = wb.sheet_names()
            sh = wb.sheet_by_index(0)
            sh = wb.sheet_by_name(sheet_name[0])
            n_rows = sh.nrows
            row = 0
            product_names = {}
            product_codes = {}
            #use in Product template
            product_name_list = []
            product_default_code_list = []
            
            product_names = self.env['product.product'].search([]).mapped('name')
            product_default_codes = self.env['product.product'].search([]).mapped('default_code')
            
            #add data in list Product template
            filter_default_codes = filter(lambda a: a != False, product_default_codes)
            product_name_list = map(lambda x:x.lower(),product_names)
            product_default_code_list = map(lambda x:x.lower(),filter_default_codes)
            
            product_names = dict(zip(product_name_list, product_names))
            product_codes = dict(zip(product_default_code_list, product_default_codes))  
            
            for r in range(1, n_rows):
                #Internal Ref.
                default_code = str(str(sh.row_values(r)[0]).split('.')[0]).strip()
                if not default_code:
                    raise UserError(_("Please add Product Code on row No. %s.")%(r+1)) 
                #Name
                name = tools.ustr(sh.row_values(r)[1])
                if not name:
                    raise UserError(_("Please add Product Name on row No. %s.")%(r+1))
                #Quantity
                qty = sh.row_values(r)[2]
                if not qty:
                    raise UserError(_("Please add Product Quantity on row No. %s.")%(r+1))
                          
                if name.lower() in product_name_list and default_code.lower() in product_default_code_list:
                    product_id = product_obj.search([('name','=',product_names[name.lower()]),
                                                    ('default_code','=',product_codes[default_code.lower()])],limit=1)
                    if product_id:
                        current_record.write({'line_ids':[(0, 0, {
                                                              'product_id':product_id.id,
                                                              'quantity':qty,
                                                              }
                                                     )],
                                        })
                elif name.lower() in product_name_list and not default_code.lower() in product_default_code_list:
                    pass
                elif default_code.lower() in product_default_code_list and not name.lower() in product_name_list:
                    pass
                else:
                    product_id = product_obj.create({
                                    'name':name,
                                    'default_code': default_code,
                                 })
                                 
                    current_record.write({'line_ids':[(0, 0, {
                                                              'product_id':product_id.id,
                                                              'quantity':qty,
                                                              }
                                                     )],
                                        })  

        #csv file
        if self.file_type == 'csv':
            if fname != 'csv':
                raise UserError(_('Please choose the file with .csv extension and proper format!'))
                
            val = base64.b64decode(self.import_file) 
            fp = StringIO.StringIO(val)
            #fp.seek(1)
            reader = csv.reader(fp, delimiter=',', quotechar='"')

            reader_info = []
            try:
                reader_info.extend(reader)
            except Exception:
                raise exceptions.Warning(_("Not a valid file!"))
            
            product_names = {}
            product_codes = {}
            #use in Product template
            product_name_list = []
            product_default_code_list = []
            
            product_names = self.env['product.product'].search([]).mapped('name')
            product_default_codes = self.env['product.product'].search([]).mapped('default_code')
            
            #add data in list Product template
            filter_default_codes = filter(lambda a: a != False, product_default_codes)
            product_name_list = map(lambda x:x.lower(),product_names)
            product_default_code_list = map(lambda x:x.lower(),filter_default_codes)
            
            product_names = dict(zip(product_name_list, product_names))
            product_codes = dict(zip(product_default_code_list, product_default_codes))
            
            #file's rows operations
            line=1    
            for row in reader_info[1:]:
                #print"row==>>",row[0],row[1],row[2]
                #Internal Ref.    
                default_code = str(row[0]).strip()
                if not default_code:
                    raise UserError(_("Please add Product Code on row No. %s.")%(line+1)) 
                #Name
                name = tools.ustr(row[1])
                if not name:
                    raise UserError(_("Please add Product Name on row No. %s.")%(line+1))
                #Quantity
                qty = row[2]
                if not qty:
                    raise UserError(_("Please add Product Quantity on row No. %s.")%(line+1))
                          
                if name.lower() in product_name_list and default_code.lower() in product_default_code_list:
                    product_id = product_obj.search([('name','=',product_names[name.lower()]),
                                                    ('default_code','=',product_codes[default_code.lower()])],limit=1)
                    if product_id:
                        current_record.write({'line_ids':[(0, 0, {
                                                              'product_id':product_id.id,
                                                              'quantity':qty,
                                                              }
                                                     )],
                                        })
                elif name.lower() in product_name_list and not default_code.lower() in product_default_code_list:
                    pass
                    #raise UserError(_("Product '%s' is already exist but Product code is different in Master Product . So, Please Change Product Code '%s' on row No.:- %s") %(name, default_code, line+1))
                
                elif default_code.lower() in product_default_code_list and not name.lower() in product_name_list:
                    pass                           
                else:
                    product_id = product_obj.create({
                                        'name':name,
                                        'default_code': default_code,
                                     })
                                     
                    current_record.write({'line_ids':[(0, 0, {
                                                              'product_id':product_id.id,
                                                              'quantity':qty,
                                                              }
                                                     )],
                                        })
                line +=1
                    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
