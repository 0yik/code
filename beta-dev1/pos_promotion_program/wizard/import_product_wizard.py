from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
import base64
import csv
import cStringIO
import tempfile
import binascii
import xlrd

class ProductImportWizard(models.TransientModel):
    _name = "product.line.import"

    file = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')

    def create_order_line(self, field):
        product_obj = self.env['product.product']
        order_line_obj = self.env['import.pos.promotion.product']
        if not str(field[0]).strip():
            raise exceptions.Warning(_("You must enter code in Product Code column"))
        product_id = product_obj.search([('default_code', '=', str(field[0]).strip())])
        print "================product_id===============",product_id
        if not product_id and not str(field[1]).strip():
            return
        if not product_id and str(field[1]).strip():
            product_id = product_obj.create({'name': field[1].strip() or '','default_code':str(field[0]).strip()})
            
        if product_id:
            order_line_obj.create({
                        'product_id': product_id.id,
                        'product_code': product_id.default_code,
                        'categ_id': product_id.pos_categ_id.id,
                        'sale_price':product_id.lst_price,
                        'line_id':self._context.get('active_id',False)
            })

    @api.multi
    def import_product_line_data(self):
        if self.import_option == 'csv':
            data = base64.b64decode(self.file)
            file_input = cStringIO.StringIO(data)
            file_input.seek(0)
            reader = csv.reader(file_input, delimiter=',',
                                lineterminator='\r\n')
            reader_info = []
            try:
                reader_info.extend(reader)
            except Exception:
                raise exceptions.Warning(_("Not a valid file!"))
            
            for i in range(1, len(reader_info)):
                try:
                    field = map(str, reader_info[i])
                except ValueError:
                    raise exceptions.Warning(_("Dont Use Character only use numbers"))
                self.create_order_line(field)
        else:
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            for row_no in range(sheet.nrows):
                val = {}
                if row_no==0:
                    continue
                if row_no <= 1:
                    field = map(lambda row:row.value, sheet.row(row_no))
                else:
                    field = (map(lambda row:isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                self.create_order_line(field)
