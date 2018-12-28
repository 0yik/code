# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import time
import tempfile
import binascii
import xlrd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
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

class sale_order(models.Model):
    _inherit = 'sale.order'

    custom_seq = fields.Boolean('Custom Sequence')
    system_seq = fields.Boolean('System Sequence')


class gen_sale(models.TransientModel):
    _name = "gen.sale"

    file = fields.Binary('File')
    sequence_opt = fields.Selection([('custom', 'Use Excel/CSV Sequence Number'), ('system', 'Use System Default Sequence Number')], string='Sequence Option',default='custom')
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')

    @api.multi
    def make_sale(self, values):
        sale_obj = self.env['sale.order']
        sale_search = sale_obj.search([
                                             ('name', '=', values.get('order'))
                                             ])
        if sale_search:
            if sale_search.partner_id.name.encode('utf-8') == values.get('customer'):
                if  sale_search.pricelist_id.name.encode('utf-8') == values.get('pricelist'):
                    lines = self.make_order_line(values, sale_search)
                    return lines
                else:
                    raise Warning(_('Pricelist is different for "%s" .\n Please define same.') % values.get('order'))
            else:
                raise Warning(_('Customer name is different for "%s" .\n Please define same.') % values.get('order'))
        
        else:
            if values.get('seq_opt') == 'system':
                name = self.env['ir.sequence'].next_by_code('sale.order')
            elif values.get('seq_opt') == 'custom':
                name = values.get('order')
            partner_id = self.find_partner(values.get('customer'))
            currency_id = self.find_currency(values.get('pricelist'))
            user_id  = self.find_user(values.get('user'))
            order_date = self.make_order_date(values.get('date'))
            sale_id = sale_obj.create({
                                        'partner_id' : partner_id.id,
                                        'pricelist_id' : currency_id.id,
                                        'name':name,
                                        'user_id': user_id.id,
                                        'date_order':order_date,
                                        'custom_seq': True if values.get('seq_opt') == 'custom' else False,
                                        'system_seq': True if values.get('seq_opt') == 'system' else False,
                                        })
            lines = self.make_order_line(values, sale_id)
            return lines

    @api.multi
    def make_order_line(self, values, sale_id):
        product_obj = self.env['product.product']
        order_line_obj = self.env['sale.order.line']
        product_search = product_obj.search([('default_code', '=', values.get('product'))])
        product_uom = self.env['product.uom'].search([('name', '=', values.get('uom'))])
        tax_ids = []
        if values.get('tax'):
            if ';' in  values.get('tax'):
                tax_names = values.get('tax').split(';')
                for name in tax_names:
                    tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
                    if not tax:
                        raise Warning(_('"%s" Tax not in your system') % name)
                    tax_ids.append(tax.id)
                
            elif ',' in  values.get('tax'):
                tax_names = values.get('tax').split(',')
                for name in tax_names:
                    tax= self.env['account.tax'].search([('name', '=', name),('type_tax_use','=','sale')])
                    if not tax:
                        raise Warning(_('"%s" Tax not in your system') % name)
                    tax_ids.append(tax.id)
            else:
                pass
        if product_search:
            product_id = product_search
        else:
            product_id = product_obj.search([('name', '=', values.get('product'))])
            if not product_id:
                product_id = product_obj.create({'name': values.get('product'),
                                                 })
        if not product_uom:
            raise Warning(_(' "%s" Product UOM category is not available.') % values.get('uom'))
        res = order_line_obj.create({
                'product_id' : product_id.id,
                'quantity' : values.get('quantity'),
                'price_unit' : values.get('price'),
                'name' : values.get('description'),
                'uom_id' : product_uom.id,
                'order_id' : sale_id.id
                })
        if tax_ids:
            res.write({'tax_id':([(6,0,[tax_ids])])})
        return True


    @api.multi
    def make_order_date(self, date):
        DATETIME_FORMAT = "%Y-%m-%d"
        i_date = datetime.strptime(date, DATETIME_FORMAT)
        return i_date



    @api.multi
    def find_user(self, name):
        user_obj = self.env['res.users']
        user_search = user_obj.search([('name', '=', name)])
        if user_search:
            return user_search
        else:
            raise Warning(_(' "%s" User is not available.') % name)


    @api.multi
    def find_currency(self, name):
        currency_obj = self.env['product.pricelist']
        currency_search = currency_obj.search([('name', '=', name)])
        if currency_search:
            return currency_search
        else:
            raise Warning(_(' "%s" Pricelist are not available.') % name)

    @api.multi
    def find_partner(self, name):
        partner_obj = self.env['res.partner']
        partner_search = partner_obj.search([('name', '=', name)])
        if partner_search:
            return partner_search
        else:
            partner_id = partner_obj.create({
                                             'name' : name})
            return partner_id

    @api.multi
    def import_sale(self):
 
        """Load Inventory data from the CSV file."""
        if self.import_option == 'csv':        
            keys = ['order', 'customer', 'pricelist','product', 'quantity', 'uom', 'description', 'price','user','tax','date']
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
            for i in range(len(reader_info)):
#                val = {}
                field = map(str, reader_info[i])
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        values.update({'option':self.import_option,'seq_opt':self.sequence_opt})
                        res = self.make_sale(values)
        else: 
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = (map(lambda row:isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    a1 = int(float(line[10]))
                    a1_as_datetime = datetime(*xlrd.xldate_as_tuple(a1, workbook.datemode))
                    date_string = a1_as_datetime.date().strftime('%Y-%m-%d')
                    values.update( {'order':line[0],
                                    'customer': line[1],
                                    'pricelist': line[2],
                                    'product': line[3],
                                    'quantity': line[4],
                                    'uom': line[5],
                                    'description': line[6],
                                    'price': line[7],
                                    'user': line[8],
                                    'tax': line[9],
                                    'date':date_string,
                                    'seq_opt':self.sequence_opt
                                    })
                    
                    res = self.make_sale(values)

                            
        return res

