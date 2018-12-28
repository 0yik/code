# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
import base64
import csv
import cStringIO
from odoo.exceptions import Warning
import tempfile
import binascii
import xlrd

class ImportBOM(models.TransientModel):
    _name = 'import.bom'

    file = fields.Binary('File ', required=True)
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='csv')

    @api.multi
    def import_bom(self, field):
        product_obj = self.env['product.product']
        product_tmpl_obj = self.env['product.template']
        bom_obj = self.env['mrp.bom']
        mrp_bom_line = self.env['mrp.bom.line']
        uom_obj = self.env['product.uom']

        product_id = product_tmpl_obj.search([('name', '=', field[0].strip())], limit=1)
        if not product_id:
            product_id = product_tmpl_obj.create({'name': field[0].strip()})

        bom_id = bom_obj.search([('product_tmpl_id', '=', product_id.id)], limit=1)

        product_uom = uom_obj.search([('name', '=', field[2].strip())])
        material_uom = uom_obj.search([('name', '=', field[5].strip())])
        if not product_uom:
            raise Warning(_('This "%s" uom is not in system, Please create it.') % field[2].strip())
        if not material_uom:
            raise Warning(_('This "%s" uom is not in system, Please create it.') % field[5].strip())

        material_id = product_obj.search([('name', '=', field[3].strip())], limit=1)
        flag = False
        if not material_id:
            material_id = product_obj.create({'name': field[3].strip()})

        if bom_id:

            for bom_line in bom_id.bom_line_ids:
                if bom_line.product_id != material_id:
                    flag = True
                if bom_line.product_id == material_id:
                    bom_line.product_qty = float(field[4].strip())
                    return

            if flag:
                mrp_bom_line.create({
                        'bom_id': bom_id.id,
                        'product_id': material_id.id,
                        'product_qty': float(field[4].strip()),
                        'product_uom_id': material_uom.id,
                        })

        else:
            variant_id = self.env['product.product'].search([('product_tmpl_id', '=', product_id.id)], limit=1)
            bom_obj.create({
                        'product_tmpl_id': product_id.id,
                        'product_id': variant_id.id,
                        'product_qty': float(field[1].strip()),
                        'product_uom_id': product_uom.id,
                        'bom_line_ids': [(0, 0, {
                                    'product_id': material_id.id,
                                    'product_qty': float(field[4].strip()),
                                    'product_uom_id': material_uom.id,
                                    })]
                        })

    @api.multi
    def import_bom_data(self):
        if self.import_option == 'xls':
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            try:
                workbook = xlrd.open_workbook(fp.name)
            except Exception:
                raise exceptions.Warning(_("Not a valid file!"))

            sheet = workbook.sheet_by_index(0)
            for row_no in range(sheet.nrows):
                if row_no <= 0:
                    fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = (map(lambda row: isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    self.import_bom(line)

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
                    raise exceptions.Warning(_("Dont Use Charecter only use numbers"))

                self.import_bom(field)
