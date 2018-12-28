from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
import base64
import csv
import cStringIO
import tempfile
import binascii
import xlrd

class OrderLineImportWizard(models.TransientModel):
    _name = "sale.order.line.import"

    file = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')

    def create_order_line(self, lines):
        product_obj = self.env['product.product']
        order_line_obj = self.env['sale.order.line']
        sale_order_obj = self.env['sale.order'].browse(self._context.get('active_id',False))
        list_create_line = []
        list_write_line = []
        for field in lines:
            if type(field[0]) == float:
                code = str(int(float(field[0])))
            else:
                code = str(field[0])
            if not code:
                raise exceptions.Warning(_("You must enter code in Product Code column"))
            product_id = product_obj.search([('default_code', '=', code)])
            if not product_id and not str(field[1]).strip():
                return
            if not product_id and str(field[1]).strip():
    #             raise exceptions.Warning(_("%s Code does not exist in the system" % (str(field[0]).strip())))
                product_id = product_obj.create({'name': field[1].strip() or '','code':code})
                product_id.product_tmpl_id.code = code
                product_id.product_tmpl_id.default_code = code
    #         if field[3].strip() not in ('percent','amount'):
    #             raise exceptions.Warning(_("Discount type must be 'percent' or 'amount'"))
            order_line_id = order_line_obj.search([('product_id','=',product_id.id),('order_id','=',self._context.get('active_id',False))])
            custom_discount_type = ''
            if field[3].strip():
                if str(field[3].strip()).lower() not in ['percent','percentage','amount']:
                    raise exceptions.Warning(_("Please enter percentage or amount in discount type column in csv/xlsx file"))
                elif str(field[3].strip()).lower() in ['percent','percentage']:
                    custom_discount_type = 'percent'
                else:
                    custom_discount_type = 'amount'
            if not order_line_id:
                # order_line_obj.create()
                list_create_line.append((0, 0, {
                            'name':product_id.name,
                            'product_id': product_id.id,
                            'product_uom':product_id.uom_id.id,
                            'code': product_id.code,
                            'custom_discount_rate':str(field[4]).strip(),
                            'product_uom_qty': float(str(field[2]).strip()),
                            'custom_discount_type': custom_discount_type,
                            'order_id':self._context.get('active_id',False)
                }))

            elif order_line_id and not field[3].strip():
                final_orderline = order_line_id.filtered(lambda o: o.custom_discount_type not in ['percent','amount'])
                if final_orderline:
                    list_write_line.append((1,final_orderline.id,{
                                        'product_uom_qty': float(final_orderline.product_uom_qty) + float(str(field[2]).strip()),
                                        'custom_discount_type': custom_discount_type,
                                        'custom_discount_rate':str(field[4]).strip(),
                    }))

            elif order_line_id and field[3].strip():
                list_create_line.append((0, 0, {
                            'name':product_id.name,
                            'product_id': product_id.id,
                            'product_uom':product_id.uom_id.id,
                            'code': product_id.code,
                            'custom_discount_rate':str(field[4]).strip(),
                            'product_uom_qty': float(str(field[2]).strip()),
                            'custom_discount_type': custom_discount_type,
                            'order_id':self._context.get('active_id',False)
                }))
        sale = sale_order_obj.write({'order_line':list_create_line})
        sale_write = sale_order_obj.write({'order_line':list_write_line})


    @api.multi
    def import_order_line_data(self):
        list_of_line = []
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
                # self.create_order_line(field)
                list_of_line.append(field)
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
                    code = sheet.row(row_no)
                    field = (map(lambda row: row.value and row.value or str(row.value), sheet.row(row_no)))
                # self.create_order_line(field)
                list_of_line.append(field)
        self.create_order_line(list_of_line)