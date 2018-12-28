# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.one
    @api.depends('size', 'ttl_ctn', 'ratio')
    def _compute_size_line(self):
        for line in self:
            size_lst = []
            if line.size and line.size != 'os':
                if line.size == '0-24m':
                    size_range = ['0-3M', '3-6M', '6-12M', '12-18M', '18-24M']
                elif line.size == '2-5y':
                    size_range = ['2T', '3T', '4T', '5T']
                elif line.size == '6-16y':
                    size_range = ['6 (S)', '8 (M)', '12 (L)', '14 (XL)', '16 (XXL)']
                elif line.size == 'xxs-xxl':
                    size_range = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL']
                elif line.size == 'xs-xxl':
                    size_range = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
                elif line.size == 'xxs-3x':
                    size_range = ['XXS', 'XS', 'S', 'M', 'L', 'XL', '1X', '2X', '3X']
                elif line.size == 'xs-3x':
                    size_range = ['XS', 'S', 'M', 'L', 'XL', '1X', '2X', '3X']
                else:
                    size_range = ['42/44', '46/48', '50/52', '54/56']
                    
                ordered_qty = 0.0
                if line.ttl_ctn and line.ratio:
                    ratio_lst = line.ratio.split(":")
                    for i in range(0, len(ratio_lst)):
                        try:
                            line_qty = float(ratio_lst[i]) * float(line.ttl_ctn)
                            ordered_qty += line_qty
                            size_lst.append({'size': size_range[i] if len(size_range) > i else '', 'qty': line_qty})
                        except:
                            raise UserError(_('Invalid Ratio Value (Ex. 1:2:3)'))
                self.product_uom_qty = ordered_qty
            self.size_line = size_lst
            
    @api.depends('product_uom_qty', 'qty_invoiced')
    def _get_outstanding_qty(self):
        for line in self:
            line.qty_outstanding = line.product_uom_qty - line.qty_invoiced

    pm_no = fields.Char("PMNo.")
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Sale Qty'), required=True, default=1.0)
    qty_outstanding = fields.Float(
        compute='_get_outstanding_qty', string='Outstanding', store=True, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    shipment_buyer_order_no = fields.Char("ShipmentBuyerOrderNo")
    product_pack_id = fields.Many2one("product.pack", string="Pack")
    company_commision = fields.Char("Company Commision")
    agent_commision = fields.Char("Agent Commision")
    colour_name = fields.Char("Color")
    col_code = fields.Char("Col Code")
    tolerance = fields.Float("Tolerance(%)", digits=(2, 0))
    shipment_ship_mode = fields.Many2one("delivery.carrier", string="ShipmentShipMode")
    shipment_delivery_date = fields.Date("ShipmentDeliveryDate")
    original_delivery_date = fields.Date("OriginalDeliveryDate")
    ref_no = fields.Many2one("product.product", string="Ref")
    asn_no = fields.Char("ASN No.")
    gender = fields.Selection([
        ('baby boy', 'BABY BOY'),
        ('baby girl', 'BABY GIRL'),
        ('toddler boy', 'TODDLER BOY'),
        ('toddler girl', 'TODDLER GIRL'),
        ('kids boy', 'KIDS BOY'),
        ('kids girl', 'KIDS GIRL'),
        ('mens', 'MENS'),
        ('ladies', 'LADIES'),
        ('na', 'NA')], string='Gender')
    fabric_id = fields.Many2one("fabric.fabric", string="Fabric ID")
    fiber_content = fields.Char("Fiber Content")
    dim_code = fields.Char("DIM Code")
    component_code = fields.Char("Component Code")
    hts_code = fields.Char("HTS Code")
    cat_no = fields.Char("Cat No")
    knitted = fields.Char("Knitted")
    note = fields.Char("Note")
    stk_issue_qty = fields.Char("Stk Issue Qty")
    stk_issue_os_qty = fields.Char("Stk Issue OS Qty")
    cost_total = fields.Float("Cost Total")
    port_of_loading = fields.Char("Port of Loading")
    port_of_discharger = fields.Char("Port of Discharger")
    final_destination = fields.Char("ShipmentFinalDestination")
    dc_no = fields.Char("DC No.")
    vessel = fields.Char("Vessel")
    bl_no = fields.Char("BL No.")
    item2 = fields.Char("Item2")
    size = fields.Selection([
        ('os', 'OS'),
        ('0-24m', '0-24M'),
        ('2-5y', '2-5Y'),
        ('6-16y', '6-16Y'),
        ('xxs-xxl', 'XXS-XXL'),
        ('xs-xxl', 'XS-XXL'),
        ('xxs-3x', 'XXS-3X'),
        ('xs-3x', 'XS-3X'),
        ('42/44-54/56', '42/44-54/56'),
        ], string='Size')
    solid_size_pack = fields.Boolean("Solid Size Pack")
    ratio = fields.Char("Ratio")
    ttl_ctn = fields.Float("TTL Ctn")
    size_line = fields.One2many('product.size', 'line_id', compute="_compute_size_line", string='Size Ratio', store=True)
    col1_name = fields.Char("Col 1 Description")
    col1_content = fields.Char("Col 1 Colour")
    col2_name = fields.Char("Col 2 Description")
    col2_content = fields.Char("Col 2 Colour")
    col3_name = fields.Char("Col 3 Description")
    col3_content = fields.Char("Col 3 Colour")
    
    currency_code = fields.Char("CurrencyCode")
    currency = fields.Char("Currency")
    destination_code = fields.Char("DestinationCode")
    destination = fields.Char("Destination")
    pm_bottom_remark = fields.Char("PMBottomRemark")
    shipment_no = fields.Char("ShipmentNo")
    shipment_ref = fields.Char("ShipmentRef")
    shipment_discharge_code = fields.Char("ShipmentPortOfDischargeCode")
    shipment_discharge = fields.Char("ShipmentPortOfDischarge")
    shipment_destination_code = fields.Char("ShipmentFinalDestinationCode")
    shipment_loading_code = fields.Char("ShipmentPortOfLoadingCode")
    shipment_loading = fields.Char("ShipmentPortOfLoading")
    ship_address = fields.Char("ShipToAddress")
    pack_seq_no = fields.Char("PackSeqNo")
    pack_line_no = fields.Char("PackLineNo")
    item_seq = fields.Char("ItemSeq")
#     item_qty_uom 
    item_buyer_order_no = fields.Char("ItemBuyerOrderNo")
    item_factory_code = fields.Char("ItemLiFungFactoryCode")
    item_factory_english = fields.Char("ItemFactoryNameInEnglish")
    item_country_code = fields.Char("ItemCountryOfOriginCode")
    item_country_origin = fields.Char("ItemCountryOfOrigin")
    item_production_country_code = fields.Char("ItemProductionCountryCode")
    item_production_country = fields.Char("ItemProductionCountry")
    item_ean_no = fields.Char("ItemEANNo")
    item_hs_code = fields.Char("ItemHSCode")
    item_hs = fields.Char("ItemHS")
    item_label = fields.Char("ItemLabel")
    attribute_seq_no = fields.Char("AttributeSeqNo")
    attribute_label = fields.Char("AttributeLabel")
    attribute_data_type = fields.Char("AttributeDataType")
    attribute_code = fields.Char("AttributeCode")
    attribute_value = fields.Char("AttributeValue")
    
    @api.multi
    @api.onchange('product_id', 'product_uom_qty')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.name = self.product_id.description_sale
            self.cost_total = self.product_id.standard_price * self.product_uom_qty
        return res
    
    @api.onchange('solid_size_pack')
    def size_pack_change(self):
        if self.solid_size_pack:
            self.ttl_ctn = 1.0
        else:
            self.ttl_ctn = 0.0
            
    @api.onchange('fabric_id')
    def onchange_fabric_id(self):
        if self.fabric_id:
            self.fiber_content = self.fabric_id.description

    @api.onchange('tolerance')
    def onchange_tolerance(self):
        if self.tolerance > 20:
            raise ValidationError(_('A Tolerance should be less than 20.'))

    @api.multi
    def duplicate_line(self):
        data = self.copy_data()
        for d in data:
            d.update({'order_id':self.order_id.id})
        if self.order_id.state == 'draft':
            sol_id = self.create(data[0])
            return {
               'type':'ir.actions.client',
               'tag':'reload',
             }
        else:
            raise UserError(_('This sale order is not in draft state.'))
        return True

class ProductSize(models.Model):
    _name = 'product.size'
    
    line_id = fields.Many2one("sale.order.line", string="Order Line")
    size = fields.Char("Size")
    qty = fields.Float("Quantity")
    
class ProductPack(models.Model):
    _name = 'product.pack'
    
    name = fields.Char("Name")

class CreatePOWizard(models.TransientModel):
    _name = 'create.po.wizard'
    
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True, domain=[('supplier', '=', True)])
    
    @api.multi
    def create_po(self):
        values = {}
        so_values_list = []
        so_line_list = self.env['sale.order.line'].browse(self._context.get('active_ids', []))
        values.update({'partner_id': self.partner_id.id,
                       'subject': self.partner_id.comment})
        for so_values in so_line_list:
            val_dict = {'partner_id': so_values.order_id.partner_id.id,
                        'partner_shipping_id': so_values.order_id.partner_shipping_id.id,
                        'partner_invoice_id': so_values.order_id.partner_invoice_id.id,
                        'opening': so_values.order_id.opening,
                        'closing': so_values.order_id.closing,
                        'projects_id': so_values.order_id.projects_id.id,
                        'season': so_values.order_id.season,
                        }
            so_values_list.append(val_dict)
        common_partner = {v['partner_id']:v for v in so_values_list}.values()
        if len(common_partner) == 1:
            values.update({'customer_id':common_partner[0].get('partner_id')})
        common_partner_ship = {v['partner_shipping_id']:v for v in so_values_list}.values()
        if len(common_partner_ship) == 1:
            values.update({'customer_shipping_id':common_partner_ship[0].get('partner_shipping_id')})
        common_partner_bill = {v['partner_invoice_id']:v for v in so_values_list}.values()
        if len(common_partner_bill) == 1:
            values.update({'customer_billing_id':common_partner_bill[0].get('partner_invoice_id')})
        common_opening = {v['opening']:v for v in so_values_list}.values()
        if len(common_opening) == 1:
            values.update({'opening':common_opening[0].get('opening')})
        common_closing = {v['closing']:v for v in so_values_list}.values()
        if len(common_closing) == 1:
            values.update({'closing':common_closing[0].get('closing')})
        common_project = {v['projects_id']:v for v in so_values_list}.values()
        if len(common_project) == 1:  #                     'port_of_discharger': line.port_of_discharger,
            values.update({'project_id':common_project[0].get('projects_id')})
        common_season = {v['season']:v for v in so_values_list}.values()
        if len(common_season) == 1:
            values.update({'supp_ref':common_season[0].get('season')})
        order_id = self.env['purchase.order'].create(values)
        for line in so_line_list:
            name = line.product_id.name_get()[0][1]
            if line.product_id.description_purchase:
                name += '\n' + line.product_id.description_purchase
            line = {'product_id': line.product_id.id,
                    'product_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.product_id.standard_price,
                    'name': line.name,
                    'date_planned': line.order_id.date_order,
                    'so_id': line.order_id.id,
                    'order_id': order_id.id,
                    'garment_size': line.size,
#                     'tolerance': line.tolerance,
                    'colour_name': line.colour_name,
                    'col_code': line.col_code,
                    'supplier_id': self.partner_id.id,
#                     'item2': line.item2,
                    'pm_no': line.pm_no,
                    'shipment_buyer_order_no': line.shipment_buyer_order_no,
                    'product_pack_id': line.product_pack_id.id,
                    'company_commision': line.company_commision,
                    'agent_commision': line.agent_commision,
                    'shipment_ship_mode': line.shipment_ship_mode.id,
                    'shipment_delivery_date': line.shipment_delivery_date,
                    'original_delivery_date': line.original_delivery_date,
                    'ref_no': line.ref_no.id,
#                     'actual_crd': line.actual_crd,
#                     'invoice_no': line.invoice_no,
                    'asn_no': line.asn_no,
                    'gender': line.gender,
                    'fabric_id': line.fabric_id.id,
                    'fiber_content': line.fiber_content,
#                     'dim_code': line.dim_code,
#                     'component_code': line.component_code,
#                     'hts_code': line.hts_code,
                    'cat_no': line.cat_no,
#                     'knitted': line.knitted,
#                     'stk_issue_qty': line.stk_issue_qty,
#                     'stk_issue_os_qty': line.stk_issue_os_qty,
#                     'cost_total': line.cost_total,
#                     'port_of_loading': line.port_of_loading,
#                     'port_of_discharger': line.port_of_discharger,
                    'final_destination': line.final_destination,
#                     'dc_no': line.dc_no,
#                     'vessel': line.vessel,
#                     'bl_no': line.bl_no,
                    'solid_size_pack': line.solid_size_pack,
                    'ratio': line.ratio,
                    'ttl_ctn': line.ttl_ctn,
                    'col1_name': line.col1_name,
                    'col1_content': line.col1_content,
                    'col2_name': line.col2_name,
                    'col2_content': line.col2_content,
                    'col3_name': line.col3_name,
                    'col3_content': line.col3_content
                    }
            self.env['purchase.order.line'].create(line)
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        action['res_id'] = order_id.id
        return action
