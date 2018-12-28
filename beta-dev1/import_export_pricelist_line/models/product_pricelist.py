# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import base64
import cStringIO
import xlwt
from io import BytesIO
from xlrd import open_workbook
from datetime import datetime,timedelta


class ExportImportSale(models.TransientModel):
    _name = 'export.import.pricelist'
    _description = 'Export Import Pricelists Item'

    import_or_export    = fields.Selection(
        [('import', 'Import'),
         ('export', 'Export'),
         ], 'Import/Export', default="import")
    export_data         = fields.Binary("Export File")
    name                = fields.Char('File Name', readonly=True)
    import_data         = fields.Binary("Import File")
    state               = fields.Selection(
                                        [('choose', 'choose'),
                                         ('get', 'get'),
                                         ('result', 'Result'),
                                         ], default='choose')
    product_not_found   = fields.Text("Product Not Found")
    product_not_found   = fields.Text("Product Not Found")
    error_log           = fields.Text("Error")
    export_error_log    = fields.Text("Export Error")
    total_not_found     = fields.Integer("Total Product Not Found", )
    line_create         = fields.Integer("Total Line Create")
    line_update         = fields.Integer("Total Line Update")
    pricelist_item_id   = fields.Boolean("Export PriceList Item ID",default=False)

    @api.multi
    def import_export_so(self):
        ctx = self._context.copy()
        active_id = ctx.get('active_id')
        pricelist_obj = self.env['product.pricelist']
        pricelist_line = self.env['product.pricelist.item']
        product_pool = self.env['product.product']
        line_create = 0
        line_update = 0
        part_pool = self.env['sequence.number.product']
        header_name = [
            'Applicable On', 'Part Number',
            'Drawing Number', 'Pricing Date',
            'Start Date', 'End Date', 'Price'
        ]
        header_name_edit = [
            'Applicable On', 'Part Number',
            'Drawing Number', 'Pricing Date',
            'Start Date', 'End Date', 'Price','Pricelist Item ID'
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
                    vals = {}
                    if rec[0]:
                        product_id = self.env['product.product'].search([('name','=',rec[0].strip())])
                        if product_id:
                            vals.update({'product_id': product_id[-1].id})
                        if 'Category: ' in rec[0]:
                            cate_id = self.env['product.category'].search([('name', '=', rec[0][10:])])
                            if cate_id:
                                vals.update({'categ_id': cate_id[-1].id})
                                vals.update({'applied_on': '2_product_category'})
                        if rec[0] == 'All Products':
                            vals.update({'applied_on': '3_global'})
                    if rec[1]:
                        part_obj = part_pool.search([('name', '=', rec[1].strip())])
                        if part_obj:
                            vals.update({'part_number_product': part_obj[-1].id})
                    if rec[2]:
                            vals.update({'drawing_number': rec[2].strip()})

                    if rec[3]:
                        if isinstance(rec[3],float):
                            date = int(float(rec[3]))
                            tempDate = datetime(1900, 1, 1)
                            deltaDays = timedelta(days=int(date) - 2)
                            pricing_date = (tempDate + deltaDays).strftime("%m/%d/%Y")
                            vals.update({'pricing_date': pricing_date})
                        else:
                            vals.update({'pricing_date': rec[3]})
                    if rec[4]:
                        if isinstance(rec[4],float):
                            date = int(float(rec[4]))
                            tempDate = datetime(1900, 1, 1)
                            deltaDays = timedelta(days=int(date) - 2)
                            pricing_date = (tempDate + deltaDays).strftime("%m/%d/%Y")
                            vals.update({'pricing_date': pricing_date})
                        else:
                            vals.update({'date_start': rec[4]})
                    if rec[5]:
                        if isinstance(rec[5],float):
                            date = int(float(rec[5]))
                            tempDate = datetime(1900, 1, 1)
                            deltaDays = timedelta(days=int(date) - 2)
                            pricing_date = (tempDate + deltaDays).strftime("%m/%d/%Y")
                            vals.update({'pricing_date': pricing_date})
                        else:
                            vals.update({'date_end': rec[5]})
                    if rec[6]:
                        vals.update({'fixed_price': rec[6]})
                       #line_obj = pricelist_line.search(
                       #[('product_id', '=', prod_obj.id),
                       # ('order_id', '=', sale_id and sale_id.id or False)
                       # ])
                    if rec[7]:
                        if isinstance(rec[7],float):
                            line = self.env['product.pricelist.item'].browse(int(rec[7]))
                            if line:
                                line[-1].write(vals)
                                line_update += 1
                        else:
                            lines = self.env['product.pricelist.item'].search(['id','=',rec[7]])
                            if lines:
                                lines[-1].write(vals)
                                line_update += 1
                    else:
                        if vals:
                            vals.update({'pricelist_id' : active_id})
                            pricelist_line.create(vals)
                            line_create += 1
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
                'res_model': 'export.import.pricelist',
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
            orders = self._context.get('active_ids')
            if self.pricelist_item_id == False:
                final_data.append(header_name)
                for order in pricelist_obj.browse(orders):
                    for line in order.item_ids:
                        # print line
                        temp_arr = []
                        temp_arr.append(line.name or '')
                        temp_arr.append(line.part_number_product and line.part_number_product.name or '')
                        temp_arr.append(line.drawing_number or '')
                        temp_arr.append(line.pricing_date or '')
                        temp_arr.append(line.date_start or '')
                        temp_arr.append(line.date_end or '')
                        temp_arr.append(line.fixed_price)
                        final_data.append(temp_arr)
            else:
                final_data.append(header_name_edit)
                for order in pricelist_obj.browse(orders):
                    for line in order.item_ids:
                        # print line
                        temp_arr = []
                        temp_arr.append(line.name or '')
                        temp_arr.append(line.part_number_product and line.part_number_product.name or '')
                        temp_arr.append(line.drawing_number or '')
                        temp_arr.append(line.pricing_date or '')
                        temp_arr.append(line.date_start or '')
                        temp_arr.append(line.date_end or '')
                        temp_arr.append(line.fixed_price)
                        temp_arr.append(line.id)
                        final_data.append(temp_arr)
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
            self.name = "%s%s" % ('pricelist_item', '.xls')
            self.state = 'get'
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'export.import.pricelist',
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

