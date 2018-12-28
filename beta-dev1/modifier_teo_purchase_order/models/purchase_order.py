# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    @api.one
    @api.depends('fabric_weight', 'fabric_width', 'fabric_usage')
    def _compute_fabric_usage(self):
        for order in self:
            order.fabric_usage_pound = (order.fabric_weight / 43.05) * ((order.fabric_width + 2) / 1000) * 2.2046 * order.fabric_usage

    @api.one
    @api.depends('order_line','fabric_weight', 'fabric_width', 'fabric_usage')
    def _compute_subtotal_summary(self):
        for order in self:
            col_code_list = list(set([x.col_code for x in order.order_line]))
            summary_list = []
            for col_code in col_code_list:
                total_amount = 0.0
                for line in order.order_line:
                    if line.col_code == col_code:
                        total_amount += line.product_qty
                summary_list.append({'po_id': order.id, 'col_code': col_code, 'price': total_amount * (order.fabric_weight / 43.05) * ((order.fabric_width + 2) / 1000) * 2.2046 * order.fabric_usage})
            order.subtotal_line = summary_list
            
    @api.depends('order_line')
    def _compute_uom_summary(self):
        for order in self:
            uom_list = list(set([x.product_uom for x in order.order_line]))
            summary_list = []
            for uom in uom_list:
                total_qty = 0.0
                for line in order.order_line:
                    if line.product_uom == uom:
                        total_qty += line.product_qty
                summary_list.append({'po_id': order.id,'uom_id': uom, 'quantity': total_qty})
            order.uom_line = summary_list

    notes = fields.Html('Terms and Conditions')
    state = fields.Selection([
        ('draft', 'RFQ Created'),
        ('verified', 'RFQ Verified'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    customer_id = fields.Many2one("res.partner", string="Customer(Buyer)", domain=[('customer', '=', True)])
    customer_shipping_id = fields.Many2one("res.partner", string="Customer Shipping")
    customer_billing_id = fields.Many2one("res.partner", string="Customer Billing")
    dely_supplier_id = fields.Many2one("res.partner", "Dely Supplier")
    subject = fields.Char("Remarks")
    opening = fields.Date("Opening")
    closing = fields.Date("Closing")
    delydate = fields.Date("DelyDate")
    paid = fields.Char("Paid")
    project_id = fields.Many2one("project.project", "Project")
    ref_ship = fields.Date("Revision", default=fields.Date.context_today)
    supp_ref = fields.Char("Season")
    
#     Summary Section
    
    fabric_weight = fields.Float("Fabric Weight")
    fabric_width = fields.Float("Fabric Width")
    fabric_usage = fields.Float("Fabric Usage(Yards)")
    fabric_usage_pound = fields.Float("Fabric Usage(Pounds)", compute='_compute_fabric_usage', store=True)
    verified_uid = fields.Many2one("res.users", "Verified By User")
    subtotal_line = fields.One2many("subtotal.summary", "po_id", compute="_compute_subtotal_summary", string="Subtotal Summary", store=True)
    uom_line = fields.One2many("uom.summary", "po_id", compute="_compute_uom_summary", string="UOM Summary", store=True)
    
    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have two PO with the POID !')
    ]
    
    @api.multi
    @api.onchange('customer_id')
    def onchange_customer_id(self):
        addr = self.customer_id.address_get(['delivery', 'invoice'])
        self.customer_shipping_id = addr['delivery'],
        self.customer_billing_id = addr['invoice']
    
    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        self.subject = self.partner_id.comment
        return res
    
    @api.multi
    def action_rfq_verify(self):
        return self.write({'state': "verified",'verified_uid': self.env.user.id})
    
    @api.multi
    def action_rfq_send(self):
        res = super(PurchaseOrder, self).action_rfq_send()
        self.write({'state': "sent"})
        return res
    
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'verified', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True
    

class SubtotalSummary(models.Model):
    _name = 'subtotal.summary'
    
    po_id = fields.Many2one("purchase.order", string="PO ID")
    col_code = fields.Char("Colour Code")
    price = fields.Float("Amount in Pounds")
    
class UOMSummary(models.Model):
    _name = 'uom.summary'
    
    po_id = fields.Many2one("purchase.order", string="PO ID")
    uom_id = fields.Many2one('product.uom', 'UOM')
    quantity = fields.Float("Total Quantity")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    @api.one
    @api.depends('weight', 'width', 'fabric_usage')
    def _compute_fabric_usage(self):
        for line in self:
            line.fabric_usage_pound = (line.weight / 43.05) * ((line.width + 2) / 1000) * 2.2046 * line.fabric_usage

    so_id = fields.Many2one("sale.order", "SOID")
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Price Unit'))
    pm_no = fields.Char("PM No.")
    shipment_buyer_order_no = fields.Char("Shipment Buyer Order No")
    product_pack_id = fields.Many2one("product.pack", string="Pack")
    
    fabric_usage = fields.Float("Fabric Usage(Yards)", digits=(5, 4))
    fabric_usage_pound = fields.Float("Fabric Usage(Pounds)", compute='_compute_fabric_usage', store=True, digits=(5, 4))
    fabric_tolerance = fields.Float("Fabric Tolerance(%)")
    
    company_commision = fields.Char("Company Commision")
    agent_commision = fields.Char("Agent Commision")
    
#     tolerance = fields.Float("Tolerance(%)", digits=(2, 1))
    fabric_quantity = fields.Float("Fabric Quantity")
    colour_name = fields.Char("Colour Name")
    col_code = fields.Char("Col Code")
    
    shipment_ship_mode = fields.Many2one("delivery.carrier", string="Shipment Ship Mode")
    shipment_delivery_date = fields.Date("Shipment Delivery Date")
    original_delivery_date = fields.Date("Original Delivery Date")
    ref_no = fields.Many2one("product.product", string="Ref")
    ref_uom = fields.Many2one('product.uom', 'Ref UOM')
#     actual_crd = fields.Char("Actual CRD")
#     invoice_no = fields.Char("Invoice No")
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
    fabric_uom_id = fields.Many2one('product.uom', 'Fabric UOM')
    fiber_content = fields.Char("Fiber Content")
#     dim_code = fields.Char("DIM Code")
#     component_code = fields.Char("Component Code")
#     hts_code = fields.Char("HTS Code")
    cat_no = fields.Char("Cat No")
#     knitted = fields.Char("Knitted")
    
    width = fields.Float("Width")
    weight = fields.Float("Weight")
    log_no = fields.Char("Log No.")
    department_id = fields.Many2one("hr.department", string="DeptID")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    supplier_id = fields.Many2one("res.partner", string="SuppID", domain=[('supplier','=',True)])
    
#     stk_issue_qty = fields.Char("Stk Issue Qty")
#     stk_issue_os_qty = fields.Char("Stk Issue OS Qty")
    
    stk_receive = fields.Char("StkReceive")
    stk_receive_qty = fields.Float("StkReceiveQty")
    
#     cost_total = fields.Float("Cost Total")
#     port_of_loading = fields.Char("Port of Loading")
#     port_of_discharger = fields.Char("Port of Discharger")
    final_destination = fields.Char("Final Destination")
#     dc_no = fields.Char("DC No.")
#     vessel = fields.Char("Vessel")
#     bl_no = fields.Char("BL No.")
    
    disc_amt = fields.Float("DiscAmt")
    disc_pct = fields.Float("DiscPct")
    end_date = fields.Date("End Date")
    taxable = fields.Boolean("Taxable")
    mpn = fields.Char("MPN")
    project_id = fields.Many2one("project.project", string="ProjectID")
    pr_id = fields.Char("PRID")
#     item2 = fields.Char("Item2")
    pr_item = fields.Char("PRItem")
    pr_item2 = fields.Char("PRItem2")
    location_id = fields.Many2one("stock.location", string="Location")
    garment_size = fields.Selection([
        ('os', 'OS'),
        ('0-24m', '0-24M'),
        ('2-5y', '2-5Y'),
        ('6-16y', '6-16Y'),
        ('xxs-xxl', 'XXS-XXL'),
        ('xs-xxl', 'XS-XXL'),
        ('xxs-3x', 'XXS-3X'),
        ('xs-3x', 'XS-3X'),
        ('42/44-54/56', '42/44-54/56'),
        ], string='Garment Size')
    size = fields.Char("Size")
    solid_size_pack = fields.Boolean("Solid Size Pack")
    ratio = fields.Char("Ratio")
    ttl_ctn = fields.Float("TTL Ctn")
    col1_name = fields.Char("Col 1 Description")
    col1_content = fields.Char("Col 1 Colour")
    col2_name = fields.Char("Col 2 Description")
    col2_content = fields.Char("Col 2 Colour")
    col3_name = fields.Char("Col 3 Description")
    col3_content = fields.Char("Col 3 Colour")

    @api.onchange('product_id')
    def onchange_product_id(self):
        qunatity = self.product_qty
        res = super(PurchaseOrderLine, self).onchange_product_id()
        self.product_qty = qunatity
        if self.product_id and self.product_id.standard_price:
            self.price_unit = self.product_id.standard_price * self.product_qty
        if self.product_id and self.product_id.description_sale:
            self.name = self.product_id.description_sale
        return res
    
    @api.onchange('fabric_id')
    def onchange_fabric_id(self):
        if self.fabric_id:
            self.fiber_content = self.fabric_id.description
            self.fabric_uom_id = self.fabric_id.uom_id
    
    @api.onchange('ref_no')
    def onchange_ref(self):
        if self.ref_no:
            self.ref_uom = self.ref_no.uom_id
            
    @api.onchange('fabric_tolerance', 'weight', 'width', 'fabric_usage')
    def onchange_tolerance(self):
        if self.weight and self.width and self.fabric_usage:
            fabric_usage_pound = (self.weight / 43.05) * ((self.width + 2) / 1000) * 2.2046 * self.fabric_usage
            if self.fabric_tolerance:
                self.fabric_quantity = float(self.product_qty) * float(fabric_usage_pound) * (1.0 + (float(self.fabric_tolerance)/ 100.0))
            else:
                self.fabric_quantity = float(self.product_qty) * float(fabric_usage_pound)
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
            raise UserError(_('This purchase order is not in draft state.'))
        return True
