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
from odoo.exceptions import Warning, UserError
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

    @api.multi
    def make_sale(self, values):
        sale_obj = self.env['sale.order']
        name = self.env['ir.sequence'].next_by_code('sale.order')
        partner_id = self.find_partner(values[0].get('customer'))
        currency_id = self.find_currency(values[0].get('pricelist'))
        user_id  = self.env.user
        order_date = self.make_order_date(values[0].get('order_date'))
        sale_id = sale_obj.create({
                                    'partner_id' : partner_id.id if partner_id else False,
                                    'pricelist_id' : currency_id.id if currency_id else 1,
                                    'name':name,
                                    'user_id': user_id.id if user_id else 1,
                                    'date_order':order_date if order_date else False,
                                    'agent_commision': values[0].get('agent_com', False),
                                    'state': 'sale',
                                    })
        lines = self.make_order_line(values, sale_id)
        return lines

    @api.multi
    def make_order_line(self, list_values, sale_id):
        product_obj = self.env['product.product']
        order_line_obj = self.env['sale.order.line']
        for values in list_values:
            product_search = product_obj.search([('default_code', '=', values.get('product'))])
            if product_search:
                product_id = product_search
            else:
                product_id = product_obj.search([('name', '=', values.get('product'))])
                if not product_id:
                    product_id = product_obj.create({'name': values.get('product'), 'description_sale': values.get('description'), 'lst_price':0.0})
                    product_id.product_tmpl_id.invoice_policy ='order'
            pack_id  = self.find_pack(values.get('pack'))
            ship_del_date = self.make_order_date(values.get('ship_del_date'))
            carrier_id  = self.find_carrier(values.get('ship_mode'))
            uom_id  = self.find_uom(values.get('uom'))
            ref_id = self.find_ref_id(values.get('ref_no'))
            res = order_line_obj.create({
                    'product_id' : product_id.id if product_id else False,
                    'name' : values.get('description', values.get('product', False)),
                    'product_pack_id': pack_id.id if pack_id else False,
                    'pm_no': values.get('pm_no', False),
                    'shipment_buyer_order_no': values.get('ship_buyer_order_no', False),
                    'product_uom_qty': values.get('ordered_qty', False),
                    'price_unit': values.get('unit_price', False),
                    'product_uom' : uom_id.id if uom_id else 1,
                    'company_commision': values.get('commision', False),
                    'agent_commision': values.get('agent_com', False),
                    'colour_name': values.get('color_name', False),
                    'col_code': values.get('col_code', False),
                    'shipment_ship_mode': carrier_id.id if carrier_id else False,
                    'shipment_delivery_date': ship_del_date,
                    'ref_no': ref_id.id if ref_id else False,
                    'asn_no': values.get('asn_no', False),
                    'gender': values.get('gender').lower() if values.get('gender') else False,
                    'size': values.get('size').lower() if values.get('size') else False,
                    'solid_size_pack': values.get('solid_size_pack', False),
                    'ratio': values.get('ratio', False),
                    'ttl_ctn': values.get('ttl_ctn', False),
                    'fiber_content': values.get('fiber_content', False),
                    'col1_name': values.get('col1_name', False),
                    'col1_content': values.get('col1_content', False),
                    'col2_name': values.get('col2_name', False),
                    'col2_content': values.get('col2_content', False),
                    'col3_name': values.get('col3_name', False),
                    'col3_content': values.get('col3_content', False),
                    'cat_no': values.get('cat_no', False),
                    'note': values.get('note', False),
                    'final_destination': values.get('final_destination', False),
                    'pm_bottom_remark': values.get('pm_bottom_remark', False),
                    'shipment_no': values.get('shipment_no', False),
                    'shipment_discharge': values.get('shipment_discharge', False),
                    'ship_address': values.get('ship_address', False),
                    'item_factory_english': values.get('item_factory_english', False),
                    'item_country_origin': values.get('item_country_origin', False),
                    'item_hs_code': values.get('item_hs_code', False),
                    'order_id' : sale_id.id
                    })
        return {'type': 'ir.actions.act_window_close'} 

    @api.multi
    def make_order_date(self, date):
        if date:
            DATETIME_FORMAT = "%Y-%m-%d"
            i_date = datetime.strptime(date, DATETIME_FORMAT)
            return i_date

    @api.multi
    def find_uom(self, name):
        if name:
            uom_obj = self.env['product.uom']
            uom_search = uom_obj.search([('name', '=', name)])
            if uom_search:
                return uom_search
            else:
                raise Warning(_(' "%s" Product UOM is not available.') % name)

    @api.multi
    def find_carrier(self, name):
        if name:
            carrier_obj = self.env['delivery.carrier']
            carrier_search = carrier_obj.search([('name', '=', name)])
            if carrier_search:
                return carrier_search
            else:
                raise Warning(_(' "%s" Delivery Method is not available.') % name)

    @api.multi
    def find_currency(self, name):
        if name:
            currency_obj = self.env['product.pricelist']
            currency_search = currency_obj.search([('name', '=', name)])
            if currency_search:
                return currency_search
            else:
                raise Warning(_(' "%s" Pricelist are not available.') % name)

    @api.multi
    def find_partner(self, name):
        if name:
            partner_obj = self.env['res.partner']
            partner_search = partner_obj.search([('name', '=', name)])
            if partner_search:
                return partner_search
            else:
                raise Warning(_(' "%s" Customer is not available in System.') % name)
            
    @api.multi
    def find_pack(self, name):
        if name:
            pack_obj = self.env['product.pack']
            pack_search = pack_obj.search([('name', '=', name)])
            if pack_search:
                return pack_search
            else:
                return pack_obj.create({'name':name})
            
    @api.multi
    def find_ref_id(self, name):
        if name:
            product_obj = self.env['product.product']
            product_search = product_obj.search([('name', '=', name)])
            if product_search:
                return product_search
            else:
                product_id = product_obj.create({
                                                 'name' : name})
                return product_id

    @api.multi
    def import_sale(self):
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        list_values = []
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        for row_no in range(sheet.nrows):
            values = {}
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = (map(lambda row:isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                order_date_string = False
                ship_del_date_string = False
                order_date = datetime.today()
                order_date_string = order_date.date().strftime('%Y-%m-%d')
                if line[8]:
                    ship_del_date = datetime(*xlrd.xldate_as_tuple(int(float(line[8])), workbook.datemode))
                    ship_del_date_string = ship_del_date.date().strftime('%Y-%m-%d')
                values.update({ 'pm_no': line[0],
                                'shipment_no': line[1].split('.')[0] if line[1] else False,
                                'ship_buyer_order_no': line[2].split('.')[0] if line[2] else False,
                                'product': line[3],
                                'description': line[4],
                                'ordered_qty': line[5],
                                'uom': line[6],
                                'unit_price': line[7],
                                'ship_del_date': ship_del_date_string,
                                'ship_mode': line[9],
                                'asn_no': line[10].split('.')[0] if line[10] else False,
                                'final_destination': line[11],
                                'shipment_discharge': line[12],
                                'ship_address': line[13],
                                'item_country_origin': line[14],
                                'item_factory_english': line[15],
                                'item_hs_code': line[16].split('.')[0] if line[16] else False,
                                'agent_com': line[17],
                                'commision': line[18],
                                'gender': line[19],
                                'ref_no': line[20],
                                'note': line[21],
                                'pm_bottom_remark': line[22],
                                'cat_no': line[23].split('.')[0] if line[23] else False,
                                'pack': line[24],
                                'size': line[25],
                                'solid_size_pack': line[26],
                                'ratio': line[27],
                                'ttl_ctn': line[28],
                                'fiber_content': line[29],
                                'col1_name': line[30].split('.')[0] if line[30] else False,
                                'col1_content': line[31].split('.')[0] if line[31] else False,
                                'col2_name': line[32].split('.')[0] if line[32] else False,
                                'col2_content': line[33].split('.')[0] if line[33] else False,
                                'col3_name': line[34].split('.')[0] if line[34] else False,
                                'col3_content': line[35].split('.')[0] if line[35] else False,
                                'col_code': line[36].split('.')[0] if line[36] else False,
                                'color_name': line[37],
                                'customer': line[38],
                                'order_date': order_date_string,
                                'pricelist': line[40],
                               })
                list_values.append(values)
        return self.make_sale(list_values)
