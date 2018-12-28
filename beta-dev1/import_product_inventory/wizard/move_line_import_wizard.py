from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
import base64
import csv
import cStringIO
from odoo import api, fields, models
import openpyxl
from tempfile import TemporaryFile
import logging

_logger = logging.getLogger(__name__)

class StockPickingLineImportWizard(models.TransientModel):
    _name = "stock.picking.line.import"

    file = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')

    def create_picking_line(self, field):
        picking_br = self.env['stock.picking'].browse(self._context.get('active_id',False))
        product_tmpl_obj = self.env['product.template']
        move_obj = self.env['stock.move']
        product_obj = self.env['product.product']
        if field[1]:
            product_tmpl_id = product_tmpl_obj.search([('code', '=', field[1])], limit=1)
        if not product_tmpl_id and field[1] and field[0]:
            product_tmpl_id = product_tmpl_obj.create({'name': field[0].strip(),'code':field[1],'default_code':field[1]})
        if product_tmpl_id:
            product_id = product_obj.search([('product_tmpl_id','=',product_tmpl_id.id)])
            move_id = move_obj.search([('product_id','=',product_id.id),('picking_id','=',self._context.get('active_id',False))], limit=1)
            if move_id:
                move_id.write({
                    'product_uom_qty': float(str(field[2]).strip()) + move_id.product_uom_qty ,
                })
            else:
                vals = ({
                            'product_id': product_id.id,
                            'name':product_id.name,
                            'code': product_tmpl_id.code,
                            'product_uom':product_id.uom_id.id or 1,
                            'product_uom_qty': float(str(field[2])),
                            'picking_id':self._context.get('active_id',False),
                            'location_id':picking_br.location_id.id,
                            'location_dest_id':picking_br.location_dest_id.id,
                })
                move_id = move_obj.create(vals)
    @api.multi
    def import_picking_line_data(self):
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
                    self.create_picking_line(field)

                except ValueError:
                    raise exceptions.Warning(_("Dont Use Character only use numbers"))
        else:
            file = self.file.decode('base64')
            excel_fileobj = TemporaryFile('wb+')
            excel_fileobj.write(file)
            excel_fileobj.seek(0)

            workbook = openpyxl.load_workbook(excel_fileobj, data_only=True)
            sheet = workbook[workbook.get_sheet_names()[0]]
            flag = 0
            for row in sheet.rows:
                field = []
                if flag != 0:
                    field.append(row[0].value)
                    field.append(row[1].value)
                    field.append(row[2].value)
                    self.create_picking_line(field)

                flag+=1