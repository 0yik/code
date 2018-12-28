# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.one
    @api.depends('order_line')
    def _compute_line_item(self):
        for order in self:
            order.line_item_discount = 0.0
            order.qty_total = 0.0
#             order.qty_issued = 0.0
            for line in order.order_line:
                order.line_item_discount += (line.price_unit * line.product_uom_qty) - line.price_subtotal
                order.qty_total += line.product_uom_qty 
#                 order.qty_issued += line.delivered
                
    @api.depends('order_line.price_total','discount','freight_pm','insure_pm')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            amount_total = discount_amount = 0.0 
            if order.discount and not order.freight_pm and not order.insure_pm:
                discount_amount = (order.discount * (amount_untaxed + amount_tax)) / 100
                amount_total = (amount_untaxed + amount_tax) - discount_amount
            if not order.discount and order.freight_pm and not order.insure_pm:
                amount_total = (amount_untaxed + amount_tax) + order.freight_pm
            if not order.discount and not order.freight_pm and order.insure_pm:
                amount_total = (amount_untaxed + amount_tax) + order.insure_pm
            if order.discount and order.freight_pm and not order.insure_pm:
                discount_amount = (order.discount * (amount_untaxed + amount_tax)) / 100
                amount_total = ((amount_untaxed + amount_tax) - discount_amount) + order.freight_pm
            if order.discount and not order.freight_pm and order.insure_pm:
                discount_amount = (order.discount * (amount_untaxed + amount_tax)) / 100
                amount_total = ((amount_untaxed + amount_tax) - discount_amount) + order.insure_pm
            if not order.discount and order.freight_pm and order.insure_pm:
                amount_total = (amount_untaxed + amount_tax) + order.freight_pm + order.insure_pm
            if order.discount and order.freight_pm and order.insure_pm:
                discount_amount = (order.discount * (amount_untaxed + amount_tax)) / 100
                amount_total = ((amount_untaxed + amount_tax) - discount_amount) + order.insure_pm + order.freight_pm
            if not order.discount and not order.freight_pm and not order.insure_pm:
                amount_total = amount_untaxed + amount_tax
                
            order.update({
                'discount_amount': discount_amount,
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_total,
            })
            
    name = fields.Char(string='Order Reference', required=True, copy=False, index=True, default=lambda self: _('New'))
    # Top Fields
    ref_no = fields.Char("Reference No.")
    projects_id = fields.Many2one("project.project", string="Project")
    employee_id = fields.Many2one("res.users", string="Employee")
    tax_id = fields.Many2one("account.tax", related='partner_id.tax_id', string="Tax")
    tax_rate = fields.Float(related='partner_id.tax_id.amount', string="Tax Rate")
    divison = fields.Char("Divison")
    buyer_name = fields.Char("BuyerName")
    agent = fields.Char("Agent")
    company_commision = fields.Char("Company Commission Pct")
    cc_auto = fields.Boolean("Apply to All")
    agent_commision = fields.Char("Agent Commission Pct")
    ac_auto = fields.Boolean("Apply to All")
    season = fields.Char("Season")
    lc_no = fields.Char("LC No.")
    shipment_buyer_order_number = fields.Char("Shipment Buyer Order Number")
    subject = fields.Char("Subject")
    opening = fields.Date("Opening")
    closing = fields.Date("Closing")
    condition_sales_code = fields.Char("ConditionsOfSalesCode")
    
    # Bottom Fields
    
    currency_id = fields.Many2one("res.currency", string="Currency")
    currency_rate = fields.Float(related='currency_id.rate')
    freight_id = fields.Char("Freight")
    insure_id = fields.Char("Insurance")
    discount = fields.Float("Discount (%)")
    discount_amount = fields.Float("Discount (%) Amount")
    freight_pm = fields.Float("+/- Freight")
    insure_pm = fields.Float("+/- Insure")
    line_item_discount = fields.Float("Line Item Disc", compute="_compute_line_item")
    qty_total = fields.Float("Qty Total", compute="_compute_line_item")
    qty_issued = fields.Float("Qty Issued", compute="_compute_line_item")
    
    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have two SO with the SOID !')
    ]
    
    @api.onchange('cc_auto','ac_auto','order_line')
    def auto_filled_onchange(self):
        for line in self.order_line:
            if self.cc_auto:
                line.company_commision = self.company_commision
            else:
                line.company_commision = False
            if self.ac_auto:
                line.agent_commision = self.agent_commision
            else:
                line.agent_commision = False
