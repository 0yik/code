from odoo import models, fields, api,_,exceptions
import base64
import cStringIO
import csv
from io import BytesIO
from xlrd import open_workbook
from datetime import datetime,timedelta,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class import_sale(models.TransientModel):
    _name = 'import.sale'

    type        = fields.Selection([('csv','CSV File'),('xls','XLS File')],string='Select',default='csv')
    file_name   = fields.Char(string='File Name')
    import_file = fields.Binary(string='File',required=True)

    @api.multi
    def import_sale(self):
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
                if field[1]:
                    product_ids = self.env['product.product'].search([('name', '=', field[1].strip())])
                    if product_ids:
                        product_id = product_ids.filtered(
                            lambda record: (record.default_code or '') == field[0].strip() or '')
                        if product_id and len(product_id) == 1:
                            if self.env.context.get('active_model', False) and self.env.context.get('active_ids',False):
                                obj = self.env[self.env.context.get('active_model', False)].browse(self.env.context.get('active_ids', False))
                                line_data = [0, 0, {
                                    'product_id': product_id.id,
                                    'price_unit': float(field[3]) or 0,
                                    'product_uom_qty': float(field[2]) or 0,
                                    'part_name' : product_id.part_name or '',
                                }]
                                if self.env.context.get('active_model', False) == 'sale.order':
                                    line_data[2].update({'product_uom': product_id.uom_id.id or False,})
                                elif self.env.context.get('active_model', False) == 'sale.requisition':
                                    line_data[2].update({'product_uom_id': product_id.uom_id.id or False,
                                                         'part_number_mitsuyoshi' : product_id.default_code or '',
                                                         'customer_pmb_no' : product_id.customer_pmb_no or '',
                                                         })
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
                    if row[1]:
                        product_ids = self.env['product.product'].search([('name','=',row[1].strip())])
                        if product_ids:
                            product_id = product_ids.filtered(lambda record:(record.default_code or '') == row[0].strip() or '')
                            if product_id and len(product_id) == 1:
                                if self.env.context.get('active_model',False) and self.env.context.get('active_ids',False):
                                    obj = self.env[self.env.context.get('active_model',False)].browse(self.env.context.get('active_ids',False))
                                    line_data = [0,0,{
                                        'product_id'    : product_id.id,
                                        'price_unit'    : float(row[3]) or 0,
                                        'product_uom_qty': float(row[2]) or 0,
                                        'part_name'     : product_id.part_name or '',
                                    }]
                                    if self.env.context.get('active_model', False) == 'sale.order':
                                        line_data[2].update({'product_uom': product_id.uom_id.id or False})
                                    elif self.env.context.get('active_model', False) == 'sale.requisition':
                                        line_data[2].update({'product_uom_id': product_id.uom_id.id or False,
                                                             'part_number_mitsuyoshi': product_id.default_code or '',
                                                             'customer_pmb_no': product_id.customer_pmb_no or '',
                                                             })
                                    final_data.append(line_data)
                        else:
                            error += 1
        if self.env.context.get('active_model', False) == 'sale.order':
            obj.write({'order_line' : final_data})
        elif self.env.context.get('active_model',False) == 'sale.requisition':
            obj.write({'line_ids': final_data})
        action = self.env['ir.actions.act_window'].browse(self.env.context.get('params',False).get('action',False))
        action['res_id'] = obj.id
        return action

