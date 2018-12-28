# -*- coding: utf-8 -*-
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

class DynamicSaleWizard(models.TransientModel):
    _name = "dynamic.sale.wizard"

    file = fields.Binary('File')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date_order = fields.Datetime(string='Order Date', required=True, default=fields.Datetime.now)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True)

    @api.multi
    def make_sale(self, values):
        sale_obj = self.env['sale.order']
        name = self.env['ir.sequence'].next_by_code('sale.order')
        partner_id = self.partner_id
        currency_id = self.pricelist_id
        user_id  = self.find_user(values[0].get('employee'))
        payment_term_id = self.find_payment_term(values[0].get('payment_terms'))
        carrier_id  = self.find_carrier(values[0].get('delivery_method'))
        tax_id  = self.find_tax(values[0].get('tax'))
        project_id  = self.find_project(values[0].get('project'))
        order_date = self.date_order
        expiration_date = self.make_order_date(values[0].get('expiration_date'))
        sale_id = sale_obj.create({
                                    'partner_id' : partner_id.id if partner_id else False,
                                    'pricelist_id' : currency_id.id if currency_id else 1,
                                    'name':name,
                                    'user_id': user_id.id if user_id else 1,
                                    'date_order':order_date if order_date else False,
                                    'validity_date':expiration_date if expiration_date else False,
                                    'payment_term_id':payment_term_id.id if payment_term_id else False,
                                    'carrier_id': carrier_id.id if carrier_id else False,
                                    'ref_no': values[0].get('ref_no', False),
                                    'company_commision': values[0].get('company_com', False),
                                    'employee_id': user_id.id if user_id else False,
                                    'tax_id': tax_id.id if tax_id else False,
                                    'tax_rate': values[0].get('tax_rate', False),
                                    'division': values[0].get('division', False),
                                    'buyer_name': values[0].get('buyer_name', False),
                                    'projects_id': project_id.id if project_id else False,
                                    'agent': values[0].get('agent', False),
                                    'agent_commision': values[0].get('agent_com', False),
                                    'season': values[0].get('season', False),
                                    'lc_no': values[0].get('lc_no', False),
                                    'shipment_buyer_order_number': values[0].get('ship_buyer_order_no', False),
                                    'subject': values[0].get('subject', False),
                                    'opening': values[0].get('opening', False),
                                    'closing': values[0].get('closing', False),
                                    'freight_id': values[0].get('freight', False), 
                                    'insure_id': values[0].get('insurance', False),
                                    'discount': values[0].get('discount', False),
                                    'discount_amount': values[0].get('discount_amount', False),
                                    'freight_pm': values[0].get('freight_plus', False),
                                    'insure_pm': values[0].get('insure_plus', False),
                                    'state': 'sale',
                                    })
        lines = self.make_order_line(values, sale_id)
        return lines

    @api.multi
    def make_order_line(self, list_values, sale_id):
        product_obj = self.env['product.product']
        order_line_obj = self.env['sale.order.line']
        product_size_obj = self.env['product.size']
        for values in list_values:
            product_search = product_obj.search([('default_code', '=', values.get('product'))])
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
                    product_id = product_obj.create({'name': values.get('product'), 'description_sale': values.get('description'), 'lst_price':0.0})
            pack_id  = self.find_pack(values.get('pack'))
            ship_del_date = self.make_order_date(values.get('ship_del_date'))
            ship_original_date = self.make_order_date(values.get('ship_original_date'))
            carrier_id  = self.find_carrier(values.get('ship_mode'))
            uom_id  = self.find_uom(values.get('uom'))
            fabric_id  = self.find_fabric(values.get('fabric_id'), values.get('fiber_content'))
            res = order_line_obj.create({
                    'product_id' : product_id.id if product_id else False,
                    'name' : values.get('description', values.get('product', False)),
                    'product_pack_id': pack_id.id if pack_id else False,
                    'pm_no': values.get('pm_no', False),
                    'shipment_buyer_order_no': values.get('ship_buyer_order_no', False),
                    'product_uom_qty': values.get('ordered_qty', False),
                    'price_unit': values.get('unit_price', False),
                    'product_uom' : uom_id.id if uom_id else 1,
                    'commision': values.get('commision', False),
                    'colour_name': values.get('color_name', False),
                    'col_code': values.get('col_code', False),
                    'shipment_ship_mode': carrier_id.id if carrier_id else False,
                    'shipment_delivery_date': ship_del_date,
                    'original_delivery_date': ship_original_date,
                    'ref_no': values.get('ref', False),
                    'actual_crd': values.get('actual_crd', False),
                    'invoice_no': values.get('invoice_no', False),
                    'asn_no': values.get('asn_no', False),
                    'gender': values.get('gender').lower() if values.get('gender') else False,
                    'col1_name': values.get('col1_name', False),
                    'col1_content': values.get('col1_content', False),
                    'col2_name': values.get('col2_name', False),
                    'col2_content': values.get('col2_content', False),
                    'col3_name': values.get('col3_name', False),
                    'col3_content': values.get('col3_content', False),
                    'fabric_id': fabric_id.id if fabric_id else False,
                    'fiber_content': values.get('fiber_content', False),
                    'discount': values.get('discount', False),
                    'cat_no': values.get('cat_no', False),
                    'note': values.get('note', False),
                    'final_destination': values.get('final_destination', False),
                    'customer_lead': values.get('delivery_lead_time', False),
                    'size': values.get('size').lower() if values.get('size') else False,
                    'solid_size_pack': values.get('solid_size_pack', False),
                    'ratio': values.get('ratio', False),
                    'ttl_ctn': values.get('ttl_ctn', False),
                    'currency': values.get('currency_id', False),
                    'currency_code': values.get('currency_code', False),
                    'condition_sales_code': values.get('condition_sales_code', False),
                    'destination_code': values.get('destination_code', False),
                    'destination': values.get('destination', False),
                    'pm_bottom_remark': values.get('pm_bottom_remark', False),
                    'shipment_no': values.get('shipment_no', False),
                    'shipment_loading': values.get('shipment_loading', False),
                    'ship_address': values.get('ship_address', False),
                    'item_buyer_order_no': values.get('item_buyer_order_no', False),
                    'item_factory_english': values.get('item_factory_english', False),
                    'item_country_origin': values.get('item_country_origin', False),
                    'item_hs_code': values.get('item_hs_code', False),
                    'order_id' : sale_id.id
                    })
            if tax_ids:
                res.write({'tax_id':([(6,0,[tax_ids])])})
        return {'type': 'ir.actions.act_window_close'} 

    @api.multi
    def make_order_date(self, date):
        if date:
            DATETIME_FORMAT = "%Y-%m-%d"
            i_date = datetime.strptime(date, DATETIME_FORMAT)
            return i_date

    @api.multi
    def find_user(self, name):
        if name:
            user_obj = self.env['res.users']
            user_search = user_obj.search([('name', '=', name)])
            if user_search:
                return user_search
            else:
                raise Warning(_(' "%s" User is not available.') % name)
    
    @api.multi
    def find_payment_term(self, name):
        if name:
            payment_obj = self.env['account.payment.term']
            payment_search = payment_obj.search([('name', '=', name)])
            if payment_search:
                return payment_search
            else:
                raise Warning(_(' "%s" Payment Term is not available.') % name)
        
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
    def find_uom(self, name):
        if name:
            uom_obj = self.env['product.uom']
            uom_search = uom_obj.search([('name', '=', name)])
            if uom_search:
                return uom_search
            else:
                raise Warning(_(' "%s" Product UOM is not available.') % name)

    @api.multi
    def find_fabric(self, name, description):
        if name:
            fabric_obj = self.env['fabric.fabric']
            fabric_search = fabric_obj.search([('name', '=', name)])
            if fabric_search:
                return fabric_search
            else:
                fabric_id = fabric_obj.create({'name' : name,
                                               'description': description})
                return fabric_id
    
    @api.multi
    def find_tax(self, name):
        if name:
            tax_obj = self.env['account.tax']
            tax_search = tax_obj.search([('name', '=', name)])
            if tax_search:
                return tax_search
            else:
                raise Warning(_(' "%s" Tax is not available.') % name)
        
    @api.multi
    def find_project(self, name):
        if name:
            project_obj = self.env['project.project']
            project_search = project_obj.search([('name', '=', name)])
            if project_search:
                return project_search
            else:
                return project_obj.create({'name':name})
        
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
    def import_sale(self):
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        list_values = []
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        fields = []
        for row_no in range(sheet.nrows):
            values = {}
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            if row_no > 0:
                line = (map(lambda row:isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                expiration_date_string = False
                opening_date_string = False
                closing_date_string = False
                ship_del_date_string = False
                ship_ori_date_string = False
                if line[fields.index('Expiration Date')] if 'Expiration Date' in fields else False:
                    expiration_date = datetime(*xlrd.xldate_as_tuple(int(float(line[fields.index('Expiration Date')] if 'Expiration Date' in fields else False)), workbook.datemode))
                    expiration_date_string = expiration_date.date().strftime('%Y-%m-%d')
                if line[fields.index('Opening')] if 'Opening' in fields else False:
                    opening_date = datetime(*xlrd.xldate_as_tuple(int(float(line[fields.index('Opening')] if 'Opening' in fields else False)), workbook.datemode))
                    opening_date_string = opening_date.date().strftime('%Y-%m-%d')
                if line[fields.index('Closing')] if 'Closing' in fields else False:
                    closing_date = datetime(*xlrd.xldate_as_tuple(int(float(line[fields.index('Closing')] if 'Closing' in fields else False)), workbook.datemode))
                    closing_date_string = closing_date.date().strftime('%Y-%m-%d')
                if line[fields.index('ShipmentDeliveryDate')] if 'ShipmentDeliveryDate' in fields else False:
                    ship_del_date = datetime(*xlrd.xldate_as_tuple(int(float(line[fields.index('ShipmentDeliveryDate')] if 'ShipmentDeliveryDate' in fields else False)), workbook.datemode))
                    ship_del_date_string = ship_del_date.date().strftime('%Y-%m-%d')
                if line[fields.index('OriginalDeliveryDate')] if 'OriginalDeliveryDate' in fields else False:
                    ship_ori_date = datetime(*xlrd.xldate_as_tuple(int(float(line[fields.index('OriginalDeliveryDate')] if 'OriginalDeliveryDate' in fields else False)), workbook.datemode))
                    ship_ori_date_string = ship_ori_date.date().strftime('%Y-%m-%d')
                shipment_no = shipment_buyer_order_no = item_buyer_order_no = item_hs_code = lc_no = invoice_no = asn_no = col_1_name = col_1_content = col_2_name = col_2_content = col_3_name = col_3_content = cat_no = col_code = False
                ship_no_value = line[fields.index('ShipmentNo')] if 'ShipmentNo' in fields else False
                if ship_no_value:
                    shipment_no = ship_no_value.split('.')[0]
                ship_buyer_no_value = line[fields.index('ShipmentBuyerOrderNo')] if 'ShipmentBuyerOrderNo' in fields else False
                if ship_buyer_no_value:
                    shipment_buyer_order_no = ship_buyer_no_value.split('.')[0]
                item_buyer_no_value = line[fields.index('ItemBuyerOrderNo')] if 'ItemBuyerOrderNo' in fields else False
                if item_buyer_no_value:
                    item_buyer_order_no = item_buyer_no_value.split('.')[0]
                item_hs_code_value = line[fields.index('ItemHSCode')] if 'ItemHSCode' in fields else False
                if item_hs_code_value:
                    item_hs_code = item_hs_code_value.split('.')[0]
                lc_no_value = line[fields.index('LC No.')] if 'LC No.' in fields else False
                if lc_no_value:
                    lc_no = lc_no_value.split('.')[0]
                invoice_no_value = line[fields.index('Invoice No')] if 'Invoice No' in fields else False
                if invoice_no_value:
                    invoice_no = invoice_no_value.split('.')[0]
                asn_no_value = line[fields.index('ASN No.')] if 'ASN No.' in fields else False
                if asn_no_value:
                    asn_no = asn_no_value.split('.')[0]
                col_1_name_value = line[fields.index('Col 1 Name')] if 'Col 1 Name' in fields else False
                if col_1_name_value:
                    col_1_name = col_1_name_value.split('.')[0]
                col_1_content_value = line[fields.index('Col 1 Content')] if 'Col 1 Content' in fields else False
                if col_1_content_value:
                    col_1_content = col_1_content_value.split('.')[0]
                col_2_name_value = line[fields.index('Col 2 Name')] if 'Col 2 Name' in fields else False
                if col_2_name_value:
                    col_2_name = col_2_name_value.split('.')[0]
                col_2_content_value = line[fields.index('Col 2 Content')] if 'Col 2 Content' in fields else False
                if col_2_content_value:
                    col_2_content = col_2_content_value.split('.')[0]
                col_3_name_value = line[fields.index('Col 3 Name')] if 'Col 3 Name' in fields else False
                if col_3_name_value:
                    col_3_name = col_3_name_value.split('.')[0]
                col_3_content_value = line[fields.index('Col 3 Content')] if 'Col 3 Content' in fields else False
                if col_3_content_value:
                    col_3_content = col_3_content_value.split('.')[0]
                cat_no_value = line[fields.index('Cat No')] if 'Cat No' in fields else False
                if cat_no_value:
                    cat_no = cat_no_value.split('.')[0]
                col_code_value = line[fields.index('Col Code')] if 'Col Code' in fields else False
                if col_code_value:
                    col_code = col_code_value.split('.')[0]
                values.update({ 'pm_no': line[fields.index('PMNo')] if 'PMNo' in fields else False,
                                'buyer_name': line[fields.index('BuyerName')] if 'BuyerName' in fields else False,
                                'division': line[fields.index('Division')] if 'Division' in fields else False,
                                'agent': line[fields.index('Agent')] if 'Agent' in fields else False,
                                'currency_id': line[fields.index('CurrencyCode')] if 'CurrencyCode' in fields else False,
                                'currency_code': line[fields.index('Currency')] if 'Currency' in fields else False,
                                'condition_sales_code': line[fields.index('ConditionsOfSalesCode')] if 'ConditionsOfSalesCode' in fields else False,
                                'destination_code': line[fields.index('DestinationCode')] if 'DestinationCode' in fields else False,
                                'destination': line[fields.index('Destination')] if 'Destination' in fields else False,
                                'pm_bottom_remark': line[fields.index('PMBottomRemark')] if 'PMBottomRemark' in fields else False,
                                'shipment_no': shipment_no,
                                'ship_mode': line[fields.index('ShipmentShipMode')] if 'ShipmentShipMode' in fields else False,
                                'ship_buyer_order_no': shipment_buyer_order_no,
                                'ship_del_date': ship_del_date_string,
                                'final_destination': line[fields.index('ShipmentFinalDestination')] if 'ShipmentFinalDestination' in fields else False,
                                'shipment_loading': line[fields.index('ShipmentPortOfLoading')] if 'ShipmentPortOfLoading' in fields else False,
                                'ship_address': line[fields.index('ShipToAddress')] if 'ShipToAddress' in fields else False,
                                'product': line[fields.index('ItemNo')] if 'ItemNo' in fields else False,
                                'description': line[fields.index('ItemDesc')] if 'ItemDesc' in fields else False,
                                'ordered_qty': line[fields.index('ItemQty')] if 'ItemQty' in fields else False,
                                'uom': line[fields.index('ItemQtyUOM')] if 'ItemQtyUOM' in fields else False,
                                'item_buyer_order_no': item_buyer_order_no,
                                'item_factory_english': line[fields.index('ItemFactoryNameInEnglish')] if 'ItemFactoryNameInEnglish' in fields else False,
                                'item_country_origin': line[fields.index('ItemCountryOfOrigin')] if 'ItemCountryOfOrigin' in fields else False,
                                'item_hs_code': item_hs_code,
                                'unit_price': line[fields.index('ItemUnitPrice')] if 'ItemUnitPrice' in fields else False,
                                'color_name': line[fields.index('Color')] if 'Color' in fields else False,
                                'order':line[fields.index('Expiration Date')] if 'Expiration Date' in fields else False,
                                'expiration_date': expiration_date_string,
                                'payment_terms': line[fields.index('Payment Terms')] if 'Payment Terms' in fields else False,
                                'delivery_method': line[fields.index('Delivery Method')] if 'Delivery Method' in fields else False,
                                'ref_no': line[fields.index('Reference No.')] if 'Reference No.' in fields else False,
                                'company_com': line[fields.index('Company Commission Pct')] if 'Company Commission Pct' in fields else False,
                                'employee': line[fields.index('Employee')] if 'Employee' in fields else False,
                                'tax': line[fields.index('Tax')] if 'Tax' in fields else False,
                                'tax_rate': line[fields.index('Tax Rate')] if 'Tax Rate' in fields else False,
                                'project': line[fields.index('Project')] if 'Project' in fields else False,
                                'agent_com': line[fields.index('Agent Commission Pct')] if 'Agent Commission Pct' in fields else False,
                                'season': line[fields.index('Season')] if 'Season' in fields else False,
                                'lc_no': lc_no,
                                'subject': line[fields.index('Subject')] if 'Subject' in fields else False,
                                'opening': opening_date_string,
                                'closing': closing_date_string,
                                'pack': line[fields.index('Pack')] if 'Pack' in fields else False,
                                'commision': line[fields.index('Commision')] if 'Commision' in fields else False,
                                'col_code': col_code,
                                'ship_original_date': ship_ori_date_string,
                                'ref': line[fields.index('Reference')] if 'Reference' in fields else False,
                                'actual_crd': line[fields.index('Actual CRD')] if 'Actual CRD' in fields else False,
                                'invoice_no': invoice_no,
                                'asn_no': asn_no,
                                'gender': line[fields.index('Gender')] if 'Gender' in fields else False,
                                'col1_name': col_1_name,
                                'col1_content': col_1_content,
                                'col2_name': col_2_name,
                                'col2_content': col_2_content,
                                'col3_name': col_3_name,
                                'col3_content': col_3_content,
                                'fabric_id': line[fields.index('Fabric ID')] if 'Fabric ID' in fields else False,
                                'fiber_content': line[fields.index('FiberContent')] if 'FiberContent' in fields else False,
                                'discount': line[fields.index('Discount(%)')] if 'Discount(%)' in fields else False,
                                'cat_no': cat_no,
                                'note': line[fields.index('Note')] if 'Note' in fields else False,
                                'tax': line[fields.index('Taxes')] if 'Taxes' in fields else False,
                                'delivery_lead_time': line[fields.index('Delivery Lead Time')] if 'Delivery Lead Time' in fields else False,
                                'size': line[fields.index('Size')] if 'Size' in fields else False,
                                'solid_size_pack': line[fields.index('Solid Size Pack')] if 'Solid Size Pack' in fields else False,
                                'ratio': line[fields.index('PackingRatio')] if 'PackingRatio' in fields else False,
                                'ttl_ctn': line[fields.index('TTL Ctn')] if 'TTL Ctn' in fields else False,
                                'freight': line[fields.index('Freight')] if 'Freight' in fields else False,
                                'insurance': line[fields.index('Insurance')] if 'Insurance' in fields else False,
                                'discount': line[fields.index('Discount(%)')] if 'Discount(%)' in fields else False,
                                'discount_amount': line[fields.index('Discount(%) Amount')] if 'Discount(%) Amount' in fields else False,
                                'freight_plus': line[fields.index('+/- Freight')] if '+/- Freight' in fields else False,
                                'insure_plus': line[fields.index('+/- Insure')] if '+/- Insure' in fields else False,
                                })
                sale_search = self.env['sale.order'].search([('name', '=', values.get('order'))])
                if sale_search:
                    res = self.make_sale(list(values))
                else:
                    list_values.append(values)
        return self.make_sale(list_values)