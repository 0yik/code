import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
from xlrd import open_workbook
import xmlrpclib
import xlrd
import os
import tempfile
import binascii
from xlwt import Workbook
import xlwt

try:
    import xmlrpclib
except ImportError:
    _logger.debug('Cannot `import xmlrpclib`.')

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
# for xls 
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
    
class gen_inv(models.TransientModel):
    _inherit = "gen.inv"
    
    @api.multi
    def import_csv(self):
        print "###import_csv"

        """Load Inventory data from the CSV file."""
        if self.import_option == 'csv': 
            """Load Inventory data from the CSV file."""
            ctx = self._context
            keys=['code', 'quantity','unit_price']
            stloc_obj = self.env['stock.location']
            inventory_obj = self.env['stock.inventory']
            product_obj = self.env['product.product']
            data = base64.b64decode(self.file)
            file_input = cStringIO.StringIO(data)
            file_input.seek(0)
            reader_info = []
            reader = csv.reader(file_input, delimiter=',')
    
            try:
                reader_info.extend(reader)
            except Exception:
                raise exceptions.Warning(_("Not a valid file!"))
            values = {}
            inventory_id = inventory_obj.create({'name':self.inv_name})
            for i in range(len(reader_info)):
                val = {}
                try:
                    field= map(str, reader_info[i])
                except ValueError:
                    raise exceptions.Warning(_("Dont Use Charecter only use numbers"))
                
    #             field = reader_info[i]
                values = dict(zip(keys, field))
                prod_lst = product_obj.search([('default_code', '=',
                                                values['code'])])
                if prod_lst:
                    val['product'] = prod_lst[0].id
                    val['quantity'] = values['quantity']
                    val['price_unit'] = values['unit_price']
                if bool(val):
                    product_uom_id=product_obj.browse(val['product']).uom_id
                    res = inventory_id.write({
                'line_ids': [(0, 0, {'price_unit':val['price_unit'],'product_id':val['product'] , 'location_id' : self.location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity']})]})
                else:
                    continue
            res = inventory_obj.with_context(ids=inventory_id).prepare_inventory()
            return res
        else:
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            
            inventory_id = self.env['stock.inventory'].create({'name':self.inv_name})
            product_obj = self.env['product.product']
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = (map(lambda row:isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    if line:
                        values.update({'code':line[0],'quantity':line[1],'unit_price':line[2]})
                        prod_lst = product_obj.search([('default_code', '=',
                                                    values['code'])])
                        if prod_lst:
                            val['product'] = prod_lst[0].id
                            val['quantity'] = values['quantity']
                            val['price_unit'] = values['unit_price']
                        if bool(val):
                            product_uom_id=product_obj.browse(val['product']).uom_id
                            res = inventory_id.write({
                        'line_ids': [(0, 0, {'price_unit':val['price_unit'],'product_id':val['product'] , 'location_id' : self.location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity']})]})
                        else:
                            continue
                    res = self.env['stock.inventory'].with_context(ids=inventory_id).prepare_inventory()
            return res
