# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    #General Information
    
#     stk_id = fields.Char("Stk ID")
    size = fields.Char("Size")
    unit_qty = fields.Char("Unit Qty (Only for UOM)")
    manu_part_no = fields.Char("Manufacturer Part No")
#     currency_id
#     preferred_supp_id = 
#     supplier
    employee_id = fields.Many2one("hr.employee", string="Employee")
    categ_id1 = fields.Many2one("product.category", string="Category1")
    categ_id2 = fields.Many2one("product.category", string="Category2")
    categ_id3 = fields.Many2one("product.category", string="Category3")
    grade = fields.Char("Grade")
    spec_from = fields.Char("Spec From")
    spec_to = fields.Char("Spec To")
    marking = fields.Char("Marking")
    location = fields.Char("Location (Default)")
#     for_sales
#     for_purchase
    print_lot_no = fields.Char("Print Lot No.")
    print_expiry = fields.Char("Print Expiry")
#     qty_ordered 
#     qty_reserverd
    qty_total_main = fields.Float("Qty Total(Main WH)")
    qty_total_all = fields.Float("Qty Total(All WH)")
#     modified_employee_id = fields.Many2one("res", string="Modified Employee")
#     modified_datetime = fields.Datetime("Modified Datetime")
    min_qty = fields.Float("Minimum Qty")
    reorder_qty = fields.Float("Reorder Qty(Alert)")
    stock_take_qty = fields.Float("Stock Take Qty")
    stock_take_date = fields.Date("Stock Take Date")
    
    #Sales Tab - Pricing
    
    list_retail_price = fields.Float("List/Retail Price")
    l5_price = fields.Float("Level 5: Highest Price")
    l4_price = fields.Float("Level 4: Price")
    l3_price = fields.Float("Level 3: Price")
    l2_price = fields.Float("Level 2: Price")
    l1_price = fields.Float("Level 1: Lowest Price")
    min_price = fields.Float("Minimum Price")
    qty_pricing = fields.Boolean("Qty - Pricing")
    
    #Invoicing Tab
    
    fixed_cost_local = fields.Float("Fixed Cost (Local)")
    fixed_cost_date = fields.Date("Fixed Cost Date")
    immdcogs = fields.Boolean("ImmdCOGS")
    avg_cost = fields.Float("Average Cost")
    cogs = fields.Float("COGS")
    taxable = fields.Boolean("Taxable")
    tax_claimable = fields.Boolean("Tax Claimable")
    total_cost_main_wh = fields.Float("Total Cost-MAIN WH")
    total_cost_all_wh = fields.Float("Total Cost-ALL WH")
    
    #Garment Tab
    
    a_b = fields.Char("A/B")
    packout = fields.Char("Packout")
    color = fields.Char("Color")
    style = fields.Char("Style")
    hts_code = fields.Char("HTSCode")
    cat_no = fields.Char("CatNo")
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
    fiber_content = fields.Char("FiberContent")
    knitted = fields.Char("Knitted")
    duty_rate_pct = fields.Char("DutyRatePct")
    brand = fields.Char("Brand")
    season = fields.Char("Season")
    partner_id = fields.Many2one("res.partner","Customer")
