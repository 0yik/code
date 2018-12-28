# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import base64
import cStringIO
import xlwt
from io import BytesIO
from xlrd import open_workbook

class ExportImportSale(models.TransientModel):
    _name = 'export.import.sale'
    _description = 'Export Import Sale Order Line'

    import_or_export = fields.Selection(
        [('import', 'Import'),
         ('export', 'Export'),
         ], 'Import/Export', default="import")
    export_data = fields.Binary("Export File")
    export_data_txt = fields.Binary("Export File")
    name_txt_file = fields.Char('File Name',readonly=True)
    name = fields.Char('File Name', readonly=True)
    import_data = fields.Binary("Import File")
    state = fields.Selection(
        [('choose', 'choose'),
         ('get', 'get'),
         ('result', 'Result'),
         ], default='choose')
    product_not_found = fields.Text("Product Not Found")
    error_log = fields.Text("Error")
    export_error_log = fields.Text("Export Error")
    total_not_found = fields.Integer("Total Product Not Found", )
    line_create = fields.Integer("Total Line Create")
    line_update = fields.Integer("Total Line Update")

    @api.multi
    def import_export_so(self):
        ctx = self._context.copy()
        active_id = ctx.get('active_id')
        sale_order_pool = self.env['sale.order']
        sale_line_pool = self.env['sale.order.line']
        product_pool = self.env['product.product']
        line_create = 0
        line_update = 0
        part_pool = self.env['sequence.number.product']
        header_name = [
            '','','','','','','','','',''
        ]
        self.ensure_one()
        if self.import_or_export == 'import':
            data = base64.b64decode(self.import_data)
            wb = open_workbook(file_contents=data)
            all_datas = []
            for s in wb.sheets():
                for row in range(s.nrows):
                    data_row = []
                    for col in range(s.ncols):
                        value = (s.cell(row, col).value)
                        data_row.append(value)
                    all_datas.append(data_row)
            for rec in all_datas:
                fields = rec
                break
            al_error = ''
            not_product_found = ''
            not_so_found = ''
            count = 0
            for rec in all_datas[1:]:
                try:
                    if not rec[1]:
                        if not not_so_found:
                            not_so_found.append = rec
                        else:
                            not_so_found += '\n' + rec
                        continue
                    if not rec[2]:
                        if not not_product_found:
                            product_not_found = rec
                        else:
                            not_product_found += '\n' + rec
                        continue
                    prod_obj = product_pool.search([('name', '=', rec[2].strip())])
                    if not prod_obj:
                        if not not_product_found:
                            product_not_found = rec
                        else:
                            product_not_found += '\n' + rec
                        continue
                    sale_id = sale_order_pool.search([('name', '=', rec[1].strip())])
                    if not sale_id:
                        if not not_so_found:
                            not_so_found.append = rec
                        else:
                            not_so_found += '\n' + rec
                        continue
                    part_obj = False
                    if rec[4].strip():
                        part_obj = part_pool.search([('name', '=', rec[4].strip())])
                    line_obj = False
                    if rec[7]:
                       #line_obj = sale_line_pool.search(
                       #[('product_id', '=', prod_obj.id),
                       # ('order_id', '=', sale_id and sale_id.id or False)
                       # ])
                       line_obj = sale_line_pool.browse(int(str(int(rec[7])).strip()))
                    if not line_obj:
                        sale_line_pool.create({
                            'product_id': prod_obj and prod_obj.id or False,
                            'order_id': sale_id and sale_id.id or False,
                            'quote_3': str(rec[3]).strip() or False,
                            'product_uom_qty': int(str(int(rec[5])).strip()) or 0,
                            'part_number_product': part_obj and part_obj.id or False,
                            'name': rec[6].strip() or False
                        })
                        line_create += 1
                    else:
                        line_obj.write({
                            'product_uom_qty': int(str(int(rec[5])).strip()) or 0,
                            'name': str(rec[6]).strip() or False,
                            'quote_3': str(rec[3]).strip() or False,
                            'part_number_product': part_obj and part_obj.id or False,
                        })
                        line_update += 1
                except Exception as e:
                    error = 'Error: %s Record: %s \n' % (e, rec)
                    al_error += error
                    continue
            self.error_log = al_error
            self.state = 'result'
            self.total_not_found = not_product_found
            self.line_update = line_update
            self.line_create = line_create
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'export.import.sale',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }

        else:
            output = cStringIO.StringIO()
            #output = BytesIO()
            all_error = ''
            book = xlwt.Workbook()
            ws = book.add_sheet('sheet-1')
            #ws.write(0, 0,  )
            final_data = []
            data_txt = ''
            final_data.append(header_name)
            orders = self._context.get('active_ids')
            self.name_txt_file = "%s%s" % ('sale_order_line', '.txt')
            filename = '/opt/odoo/sale_order_line.txt'
            file = open(filename, "w")
            for order in sale_order_pool.browse(orders):
                for line in order.order_line:
                    print line
                    temp_arr = []
                    temp_txt = ''
                    # temp_arr.append(order.id)
                    # temp_arr.append(order.name)
                    # temp_arr.append(line.product_id.name)
                    # temp_arr.append(line.quote_3 or '')
                    if line.part_number_product:
                        temp_arr.append(line.part_number_product.name)
                        temp_txt += (str(line.part_number_product.name.encode('utf-8')) + ',')
                    else:
                        temp_arr.append('')
                        temp_txt +=('' +',')
                    # temp_arr.append(line.product_uom_qty or 0)
                    # temp_arr.append(line.name or '')
                    # temp_arr.append(line.id)
                    temp_arr.append(line.part_name or '')
                    temp_txt +=(str(line.part_name and line.part_name.encode('utf-8') or '') +',')
                    temp_arr.append(line.add_name_1 or '')
                    temp_txt +=(str(line.add_name_1 or '') +',')
                    temp_arr.append(line.add_name_2 or '')
                    temp_txt +=(str(line.add_name_2 or '') +',')
                    temp_arr.append(line.drawing_number or '')
                    temp_txt +=(str(line.drawing_number and line.drawing_number.encode('utf-8') or '') +',')
                    temp_arr.append(order.revision or '')
                    temp_txt +=(str(order.revision or '') +',')
                    if order.partner_id:
                        temp_arr.append(order.partner_id.partner_code or '')
                        temp_txt +=(str(order.partner_id.partner_code.encode('utf-8') or '') +',')
                    else:
                        temp_arr.append('')
                        temp_txt +=('' +',')
                    temp_arr.append(line.price_unit or 0.0)
                    temp_txt +=(str(line.price_unit or 0.0) + ',')
                    temp_arr.append(line.coating_en and line.coating_en.name or '')
                    temp_txt +=(str(line.coating_en and line.coating_en.name.encode('utf-8') or '') +',')
                    temp_arr.append('2')
                    temp_txt +=('2' +'\n')
                    final_data.append(temp_arr)
                    # data_txt += str(temp_txt.encode('utf-8'))
                    file.write(temp_txt)
            # HEADER WRITE
           #row , col = 0, 0
           #for header_nam in final_data:
           #    print "fffffffffff",header_nam
           #    for j, t in enumerate(header_nam):
           #        if row == 0 and col == 0:
           #            ws.write(0, 0 + j, t)
           #        else:
           #            ws.write(row + 1, col + j, t)
            for i, l in enumerate(final_data):
                for j, col in enumerate(l):
                    ws.write(i, j, col)
            book.save(output)
            self.export_data = base64.b64encode(output.getvalue())
            self.name = "%s%s" % ('sale_order_line', '.xls')
            self.state = 'get'
            file.close()
            with open(filename, "r") as file:
                self.export_data_txt = base64.b64encode(file.read())
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'export.import.sale',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }

    @api.multi
    def action_done(self):
        return {
            'type': 'ir.actions.act_window_close'
        }

