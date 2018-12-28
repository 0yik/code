# -*- coding: utf-8 -*-

from odoo import fields, models
import base64
from xml.etree import ElementTree
from xml.etree.ElementTree import Element,SubElement
from xml.dom import minidom
from odoo.tools.misc import ustr
import datetime

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    each = fields.Char("Each")
    setup = fields.Char("setup")
    alloy = fields.Char("Alloy")

class SaleOrder(models.Model):
    _inherit = "sale.order"

    buyer_comment = fields.Char('Buyer Comment')
    transport_payer = fields.Char('Transport Payer')
    customer_transport_time_days = fields.Char('Customer Transport time Days')
    customer_invoice_code = fields.Char('Customer Invoice Code')
    buyer_reference = fields.Char('Buyer Reference')

    def download_xml(self):
        order_ids = self._context.get('active_ids',[])
        if order_ids:
            Orders = Element('ORDERS420')#Top Element
            Orders.set('SoftwareManufacturer',ustr('Monitor ERP System AB'))
            Orders.set('SoftwareName',ustr('Monitor'))
            Orders.set('SoftwareVersion',ustr('8.0.12p39'))
            
            for order in self.env['sale.order'].browse(order_ids):
                Order = SubElement(Orders,'Order')
                Order.set('OrderNumber',ustr(str(order.po_num) or ''))
                
                head = SubElement(Order,'Head')#Header Part
                
                supplier = SubElement(head, 'Supplier')#Supplier (Company Address)
                supplier.set('SupplierCodeEdi','123')#FixMe
                supplier_name = SubElement(supplier, 'Name')
                supplier_name.text = ustr(order.user_id.company_id.name)
                
                StreetBox1 = SubElement(supplier, 'StreetBox1')
                if order.user_id.company_id.street:
                    StreetBox1.text = ustr(order.user_id.company_id.street)
                    
                StreetBox2 = SubElement(supplier, 'StreetBox2')
                if order.user_id.company_id.street2:
                    StreetBox2.text = ustr(order.user_id.company_id.street2)
                    
                ZipCity1 = SubElement(supplier, 'ZipCity1')
                if order.user_id.company_id.city:
                    ZipCity1.text = ustr(order.user_id.company_id.city) +' ' + ustr(order.user_id.company_id.state_id.name or '')
                    
                ZipCity2 = SubElement(supplier, 'ZipCity2')
                if order.user_id.company_id.zip:
                    ZipCity2.text = ustr(order.user_id.company_id.zip)
                    
                Country = SubElement(supplier, 'Country')
                if order.user_id.company_id.country_id:
                    Country.text = ustr(order.user_id.company_id.country_id.name)
                    
                Buyer = SubElement(head, 'Buyer')#Customer Address
                Buyer_name = SubElement(Buyer, 'Name')
                Buyer_name.text = ustr(order.partner_id.name)
                
                StreetBox1 = SubElement(Buyer, 'StreetBox1')
                if order.partner_id.street:
                    StreetBox1.text = ustr(order.partner_id.street)
                    
                StreetBox2 = SubElement(Buyer, 'StreetBox2')
                if order.partner_id.street2:
                    StreetBox2.text = ustr(order.partner_id.street2)
                    
                ZipCity1 = SubElement(Buyer, 'ZipCity1')
                if order.partner_id.city:
                    ZipCity1.text = ustr(order.partner_id.city or '') +' ' + ustr(order.partner_id.state_id.name or '') +' ' + ustr(order.partner_id.zip or '')
                    
                ZipCity2 = SubElement(Buyer, 'ZipCity2')
                if order.partner_id.zip:
                    ZipCity2.text = ustr(order.partner_id.city2_mailing) +' '+ ustr(order.partner_id.state_id2.name) + ' ' + ustr(order.partner_id.zip2_mailing or '')
                    
                Country = SubElement(Buyer, 'Country')
                if order.partner_id.country_id:
                    Country.text = ustr(order.partner_id.country_id.name)
                    
                References = SubElement(head, 'References')#References    
                BuyerReference = SubElement(References, 'BuyerReference')
                BuyerReference.text = ustr(order.buyer_reference or '')
                
                BuyerComment = SubElement(References, 'BuyerComment')
                BuyerComment.text = ustr(order.buyer_comment or '')
                
                GoodsLabeling = SubElement(References, 'GoodsLabeling')
                GoodsLabeling_row1 = SubElement(GoodsLabeling,'Row1')
                GoodsLabeling_row1.text = ustr(str(order.po_num) or '')
                GoodsLabeling_row2 = SubElement(GoodsLabeling,'Row2')
                
                DeliveryAddress = SubElement(head, 'DeliveryAddress')#Delivery Address #FixMe: Need to confirm which value?
                DeliveryAddress_name = SubElement(DeliveryAddress, 'Name')
                DeliveryAddress_name.text = ustr(order.partner_shipping_id.name)
                
                StreetBox1 = SubElement(DeliveryAddress, 'StreetBox1')
                if order.partner_shipping_id.street_delivery:
                    StreetBox1.text = ustr(order.partner_shipping_id.street_delivery)
                    
                StreetBox2 = SubElement(DeliveryAddress, 'StreetBox2')
                if order.partner_shipping_id.street2_delivery:
                    StreetBox2.text = ustr(order.partner_shipping_id.street2_delivery)
                    
                ZipCity1 = SubElement(DeliveryAddress, 'ZipCity1')
                if order.partner_shipping_id.city_delivery:
                    ZipCity1.text = ustr(order.partner_shipping_id.city_delivery or '') +' ' + ustr(order.partner_shipping_id.state_id_delivery.name or '') + ' ' + ustr(order.partner_shipping_id.zip_delivery or '')
                    
                ZipCity2 = SubElement(DeliveryAddress, 'ZipCity2')
                if order.partner_shipping_id.city2_delivery:
                    ZipCity2.text = ustr(order.partner_shipping_id.city2_delivery or '') + ' ' + ustr(order.partner_shipping_id.state_id2_delivery.name or '') + ' ' + ustr(order.partner_shipping_id.zip2_delivery or '')
                    
                Country = SubElement(DeliveryAddress, 'Country')
                if order.partner_shipping_id.country_id:
                    Country.text = ustr(order.partner_shipping_id.country_id.name)
                CompanyAdressFlag = SubElement(DeliveryAddress, 'CompanyAdressFlag')
                CompanyAdressFlag.text = ustr(order.company_id.id)
                
                Terms = SubElement(head, 'Terms')#Terms
                DeliveryTerms = SubElement(Terms, 'DeliveryTerms')
                IncoTermCombiTerm = SubElement(DeliveryTerms, 'IncoTermCombiTerm')
                if order.incoterm:
                    IncoTermCombiTerm.text = ustr(order.incoterm.name or '')
                DeliveryMethod = SubElement(DeliveryTerms, 'DeliveryMethod')
                DeliveryMethod.text = ustr(order.carrier_id.name or '')
                TransportPayer = SubElement(DeliveryTerms, 'TransportPayer')
                TransportPayer.text = ustr(order.transport_payer or '')
                CustomerTransportTimeDays = SubElement(DeliveryTerms, 'CustomerTransportTimeDays')
                CustomerTransportTimeDays.text = ustr(order.customer_transport_time_days or '')
                CustomerInvoiceCode = SubElement(Terms, 'CustomerInvoiceCode')
                CustomerInvoiceCode.text = ustr(order.customer_invoice_code or '')
                OrderDate = SubElement(Terms, 'OrderDate')
                if order.order_date:
                    OrderDate.text = ustr(order.order_date).split(' ')[0]
                    
                PaymentTerms = SubElement(Terms, 'PaymentTerms')
                
                TermsOfPaymentDays = SubElement(PaymentTerms, 'TermsOfPaymentDays')
                if order.payment_term_id:
                    TermsOfPaymentDays.text = ustr(order.payment_term_id.name)
                    
                Export = SubElement(head, 'Export')#Export
                Currency = SubElement(Export, 'Currency')
                if order.pricelist_id.currency_id:
                    Currency.text = ustr(order.pricelist_id.currency_id.name)
                Rows = SubElement(Order,'Rows')#Line Items
                line_no = 1
                row_type = 1
                for line in order.order_line:
                    Row = SubElement(Rows,'Row')
                    Row.set('RowNumber',ustr(line_no))
                    Row.set('RowType',ustr(row_type))#FixMe
                    line_no+=1
                    
                    Part = SubElement(Row,'Part')
                    if line.product_id and line.product_id.part_number:
                        Part.set('PartNumber','')
                    else:
                        Part.set('PartNumber','')
                    if line.product_id and line.part_number_product:
                        Part.set('SupplierPartNumber',ustr(line.part_number_product.name))
                    else:
                        Part.set('SupplierPartNumber','')
                    
                    Text = SubElement(Row,'Text')
                    Text.text = ustr(line.product_id.name or line.name)
                    
                    ReferenceNumber = SubElement(Row,'ReferenceNumber')
                    if line.product_id.default_code:
                        ReferenceNumber.text = ustr(line.product_id.default_code)
                    
                    Quantity = SubElement(Row,'Quantity')
                    Quantity.text = ustr(str(int(line.product_uom_qty)))
                    
                    Unit = SubElement(Row,'Unit')
                    Unit.text = ustr(line.product_uom.name)
                    
                    DeliveryPeriod = SubElement(Row,'DeliveryPeriod')
                    currentDT = datetime.datetime.now()
                    date = currentDT.strftime("%m/%d/%Y")
                    DeliveryPeriod.text = ustr(date)
                    
                    Each = SubElement(Row,'Each')
                    Each.text = ustr(str(int(line.price_unit or '')))
                    
                    Discount = SubElement(Row,'Discount')
                    Discount.text = ustr(str(int(line.discount)))
                    
                    Setup = SubElement(Row,'Setup')
                    Setup.text = ustr(line.setup or 0)
                    
                    Alloy = SubElement(Row,'Alloy')
                    Alloy.text = ustr(line.alloy or 0)
                    
            filename = '/opt/odoo/Sale Order XML.xml'
            f = open(filename, 'w')
            orders = ElementTree.tostring(Orders,encoding="utf-8")
            data = minidom.parseString(orders).toprettyxml(encoding="utf-8")
            f.write(data)
            f.close()
            file_base64 = ''
            with open(filename, "r",) as file:
                file_base64 = base64.b64encode(file.read())
            export_id = self.env['so.xml.file'].create({
                                                    'xml_file': file_base64,
                                                    'file_name': filename,
                                                    })
            return {
                    'view_mode': 'form',
                    'res_id': export_id.id,
                    'res_model': 'so.xml.file',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'context': self._context,
                    'target': 'new',
                    }

