from odoo import models, fields, api,_,exceptions
import base64
import cStringIO
import csv
from io import BytesIO
from xlrd import open_workbook
from datetime import datetime,timedelta,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class import_product_line(models.TransientModel):
    _name = 'import.product.line'

    type        = fields.Selection([('csv','CSV File'),('xls','XLS File')],string='Select',default='csv')
    file_name   = fields.Char(string='File Name')
    import_file = fields.Binary(string='File',required=True)

    @api.multi
    def import_product_line(self):
        if self.file_name.split('.')[-1] not in ['xls','csv']:
            raise Warning(_('Import File should be csv or xls'))
        obj = self.env[self.env.context.get('active_model', False)].browse(self.env.context.get('active_ids', False))
        data = base64.b64decode(self.import_file)
        final_data = []
        if self.file_name.split('.')[-1] == 'csv':
            file_input = cStringIO.StringIO(data)
            file_input.seek(0)
            reader = csv.reader(file_input, delimiter=',',lineterminator='\r\n')
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
                if field[0]:
                    product_ids = self.env['product.product'].search([('default_code', '=', field[0].strip())])
                    if product_ids:
                            if self.env.context.get('active_model', False) and self.env.context.get('active_ids',False):
                                obj = self.env[self.env.context.get('active_model', False)].browse(self.env.context.get('active_ids', False))
                                line_data = [0, 0, {
                                    'product_id': product_ids[0].id,
                                    'product_uom_id': product_ids[0].uom_id.id,
                                    'product_qty': float(field[1])  or 0,
                                    'location_id': self.env['stock.inventory.line'].default_get(['location_id']) or 1
                                }]
                                if self.env.context.get('active_model', False) == 'stock.multi.reordering':
                                    line_data = [0,0,{
                                        'code'      : field[0].strip(),
                                        'product_id': product_ids[0].id,
                                        'categ_id'  : product_ids[0].categ_id.id or False,
                                        'movement'  : product_ids[0].product_tmpl_id.movement or False,
                                        'product_uom'  : product_ids[0].uom_id.id or False,
                                        'product_min_qty' : float(field[1])  or 0,

                                    }]
                                final_data.append(line_data)
        elif self.file_name.split('.')[-1] == 'xls':
            wb = open_workbook(file_contents=data)
            sheet = wb.sheet_by_index(0)
            count = 0
            error = 0
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    header = (
                    map(lambda row: isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value),
                        sheet.row(row_no)))
                else:
                    row = (
                    map(lambda row: isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value),
                        sheet.row(row_no)))
                    product_ids = []
                    if row[0]:
                        default_code= row[0].strip()
                        if ('.' in row[0].strip()) or ('+' in row[0].strip()) or ('e' in row[0].strip())or ('-' in row[0].strip()):
                            try:
                                default_code = str(long(float(row[0])))
                            except:
                                default_code = row[0].strip()
                        product_ids = self.env['product.product'].search([('default_code','=',default_code)])
                        if product_ids:

                            if self.env.context.get('active_model',False) and self.env.context.get('active_ids',False):
                                obj = self.env[self.env.context.get('active_model',False)].browse(self.env.context.get('active_ids',False))
                                line_data = [0,0,{
                                    'product_id'    : product_ids[0].id,
                                    'product_uom_id': product_ids[0].uom_id.id,
                                    'product_qty'   : float(row[1]) or 0,
                                    'location_id'   : self.env['stock.inventory.line'].default_get(['location_id']) or 1
                                }]
                                if self.env.context.get('active_model', False) == 'stock.multi.reordering':
                                    line_data = [0,0,{
                                        'code'      : default_code,
                                        'product_id': product_ids[0].id,
                                        'categ_id'  : product_ids[0].categ_id.id or False,
                                        'movement'  : product_ids[0].product_tmpl_id.movement or False,
                                        'product_uom'  : product_ids[0].uom_id.id or False,
                                        'product_min_qty' : float(row[1])  or 0,

                                    }]
                                final_data.append(line_data)

                        else:
                            error += 1
        if self.env.context.get('active_model', False) == 'stock.inventory':
            obj.write({'line_ids' : final_data})
        elif self.env.context.get('active_model',False) == 'stock.multi.reordering':
            obj.write({'line_ids': final_data})
        action = self.env['ir.actions.act_window'].browse(self.env.context.get('params',False).get('action',False))
        action['res_id'] = obj.id
        return action

