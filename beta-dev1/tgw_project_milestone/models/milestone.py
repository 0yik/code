# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class VendorType(models.Model):
    _name = 'vendor.type'

    name = fields.Char(string='Vendor Type', required=False)
    type = fields.Selection([('internal', 'Internal'), ('external', 'External')], string='Internal / External')
    service_charged = fields.Many2many('product.category', string='Services charged')

class MilestoneVendors(models.Model):
    _name = 'milestone.vendors'

    milestone_id = fields.Many2one("milestone.milestone")
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier', '=', True)])
    vendor_type = fields.Many2one('vendor.type', string="Vendor Type")
    service_charged = fields.Many2many(related='vendor_type.service_charged')
    check_intime = fields.Datetime('Check In Time')

class Milestone(models.Model):
    _inherit = 'milestone.milestone'

    contract_id = fields.Many2one('account.analytic.account', string="Contract")
    contract_number = fields.Char(related="contract_id.contract_number", string="Contract")
    
    involve_vendor = fields.Boolean(string='Involve Vendor')
    milestone_vendor_ids = fields.One2many('milestone.vendors', 'milestone_id', string='Milestone Vendor')

    # remove comment if infuture if needed this code
    # involve_staff = fields.Boolean(string='Involve Staff', default=False)
    # milestone_staffs = fields.Many2many('hr.employee', string="Milestone Staff")

    involve_product = fields.Boolean('Booked Products')
    milestone_products = fields.Many2many('product.product')
    milestone_contract_bookings_id = fields.Many2one('milestone.contract.bookings', string='Milestone Contract Bookings')