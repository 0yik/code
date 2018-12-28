from odoo import models, fields, api, tools, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
import base64
import csv
import cStringIO
import openpyxl
import tempfile
from datetime import datetime
import binascii
import xlrd
import logging
_logger = logging.getLogger(__name__)


class OrderLineImportWizard(models.TransientModel):
    _name = "purchase.order.line.import"

    file = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')

    def create_order_line(self, fields, product_tmpl_obj ,order_line_obj, product_obj):
        order_id = self.env['purchase.order'].search([('id','=',self._context.get('active_id',False))])
        fpos = order_id.fiscal_position_id
        total = 0.0
        amount_tax = 0.0
        for field in fields:
            _logger.info(" field %s " % (str(field)) )
            product_tmpl_id = product_tmpl_obj.search([('code', '=', field[1])], limit=1)
            if not product_tmpl_id and field[1] and field[0]:
                product_tmpl_id = product_tmpl_obj.create({'name': field[0].strip(),'code':field[1],'default_code':field[1]})
            if product_tmpl_id:
                product_id = product_obj.search([('product_tmpl_id','=',product_tmpl_id.id)])
                order_line_id = order_line_obj.search([('product_id','=',product_id.id),('order_id','=',self._context.get('active_id',False))], limit=1)
                if order_line_id and order_line_id.price_unit == float(str(field[3])):
                    order_line_id.write({
                            'product_qty': float(str(field[2])) + order_line_id.product_qty,
                            'price_unit':float(str(field[3])),
                    })
                else:
                    if self.env.uid == SUPERUSER_ID:
                        company_id = self.env.user.company_id.id
                        taxes_id = fpos.map_tax(product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
                    else:
                        taxes_id = fpos.map_tax(product_id.supplier_taxes_id)
                    taxes = taxes_id.compute_all(field[3], order_id.currency_id, float(str(field[2])), product=product_id, partner=order_id.partner_id)
                    total += taxes['total_excluded']
                    name = "'"+ (product_id.name.find("'") != -1  and  str(product_id.name.replace("'", "''") ) or product_id.name.encode('utf-8')) + "'"
                    self.env.cr.execute('''insert into purchase_order_line (product_id, name,product_uom, product_qty, price_unit, order_id, date_planned, price_tax, price_total, price_subtotal) values(%s, %s, %s, %s,%s, %s,%s, %s, %s, %s)    RETURNING id;'''%( product_id.id, name, product_id.uom_po_id.id, float(str(field[2])), field[3], self._context.get('active_id',False), "(now() at time zone 'UTC')", (taxes['total_included'] - taxes['total_excluded']), taxes['total_included'], taxes['total_excluded']))
                    line_id = self.env.cr.fetchone()[0]
                    for tax in taxes_id:
                        self.env.cr.execute('''insert into account_tax_purchase_order_line_rel (purchase_order_line_id, account_tax_id) values(%s, %s)'''%(line_id, tax.id))
    
                    if order_id.company_id.tax_calculation_rounding_method == 'round_globally':
                        order_taxes = taxes_id.compute_all(taxes['total_excluded'], order_id.currency_id, float(str(field[2])), product=product_id, partner=order_id.partner_id)
                        amount_tax += sum(t.get('amount', 0.0) for t in order_taxes.get('taxes', []))
                    else:
                        amount_tax += (taxes['total_included'] - taxes['total_excluded'])
                    self.env.invalidate_all()

        order_id.amount_untaxed = order_id.currency_id.round(total)
        order_id.amount_tax = order_id.currency_id.round(amount_tax)
        order_id.amount_total = order_id.currency_id.round(total) + order_id.currency_id.round(amount_tax)

    @api.multi
    def import_order_line_data(self):
        product_tmpl_obj = self.env['product.template']
        order_line_obj = self.env['purchase.order.line']
        product_obj = self.env['product.product']
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
            fields = []
            for i in range(1, len(reader_info)):
                try:
                    field = map(str, reader_info[i])
                    fields.append(field)

                except ValueError:
                    raise exceptions.Warning(_("Dont Use Character only use numbers"))
            self.create_order_line(fields,product_tmpl_obj ,order_line_obj, product_obj)
        else:
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            fields = []
            for row_no in range(1,sheet.nrows):
                # print ".........row_no ", row_no
                field = map(lambda row:row.value, sheet.row(row_no))
                if field:
                    fields.append(field)
            self.create_order_line(fields, product_tmpl_obj ,order_line_obj, product_obj)



# class OrderLineImportWizard(models.TransientModel):
#     _name = "purchase.order.line.import"

#     file = fields.Binary('File')
#     import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')

#     def create_order_line(self, fields, product_tmpl_obj ,order_line_obj, product_obj):
#         for field in fields:
#             product_tmpl_id = product_tmpl_obj.search([('code', '=', field[1])], limit=1)
#             if not product_tmpl_id and field[1] and field[0]:
#                 product_tmpl_id = product_tmpl_obj.create({'name': field[0].strip(),'code':field[1],'default_code':field[1]})
#             if product_tmpl_id:
#                 product_id = product_obj.search([('product_tmpl_id','=',product_tmpl_id.id)])
#                 order_line_id = order_line_obj.search([('product_id','=',product_id.id),('order_id','=',self._context.get('active_id',False))], limit=1)
#                 if order_line_id and order_line_id.price_unit == float(str(field[3])):
#                     vals = ({
#                             'product_qty': float(str(field[2])) + order_line_id.product_qty,
#                             'price_unit':float(str(field[3])),
#                     })
#                     order_line_id.write(vals)
#                 else:
#                     vals = ({
#                                 'product_id': product_id.id,
#                                 'name':product_id.name,
#                                 'product_code': product_tmpl_id.code,
#                                 'product_uom':product_id.uom_po_id.id,
#                                 'product_qty': float(str(field[2])),
#                                 'price_unit': field[3],
#                                 'order_id':self._context.get('active_id',False),
#                                 'date_planned':datetime.today()
#                     })

#                     line_id = order_line_obj.create(vals)

#     @api.multi
#     def import_order_line_data(self):
#         product_tmpl_obj = self.env['product.template']
#         order_line_obj = self.env['purchase.order.line']
#         product_obj = self.env['product.product']
#         if self.import_option == 'csv':
#             data = base64.b64decode(self.file)
#             file_input = cStringIO.StringIO(data)
#             file_input.seek(0)
#             reader = csv.reader(file_input, delimiter=',',
#                                 lineterminator='\r\n')
#             reader_info = []
#             try:
#                 reader_info.extend(reader)
#             except Exception:
#                 raise exceptions.Warning(_("Not a valid file!"))
#             fields = []
#             for i in range(1, len(reader_info)):
#                 try:
#                     field = map(str, reader_info[i])
#                     fields.append(field)

#                 except ValueError:
#                     raise exceptions.Warning(_("Dont Use Character only use numbers"))
#             self.create_order_line(fields,product_tmpl_obj ,order_line_obj, product_obj)
#         else:
#             fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
#             fp.write(binascii.a2b_base64(self.file))
#             fp.seek(0)
#             workbook = xlrd.open_workbook(fp.name)
#             sheet = workbook.sheet_by_index(0)
#             fields = []
#             for row_no in range(1,sheet.nrows):
#                 # print ".........row_no ", row_no
#                 field = map(lambda row:row.value, sheet.row(row_no))
#                 if field:
#                     fields.append(field)
#             self.create_order_line(fields, product_tmpl_obj ,order_line_obj, product_obj)

