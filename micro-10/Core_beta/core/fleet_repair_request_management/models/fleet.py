# -*- coding: utf-8 -*-

from odoo import fields, models

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
#     fleet_repair_id = fields.Many2one(
#         'fleet.request',
#         string='Repair Reference',
#         readonly=True,
#         copy=False,
#     )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer"
    )
    fleet_repair_ids = fields.One2many(
        'fleet.request',
        'vehicle_id',
        string='Repair Reference',
        readonly=True,
        copy=False,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product Related',
        copy=False,
    )

class FleetVehicleLogService(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    
    fleet_repair_id = fields.Many2one(
        'fleet.request',
        string='Repair Reference',
        readonly=True,
        copy=False,
    )

class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'
    
    service_charges = fields.Float(
        string='Charges',
        copy=False,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default= lambda self: self.env.user.company_id.currency_id.id,
        string='Currency', 
    )