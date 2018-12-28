# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def _get_default_team_id(self):
        return self.env.ref('maintenance.equipment_team_maintenance', raise_if_not_found=False)

    @api.multi
    def _get_no_maintenances(self):
        if self.maintenance_ids:
            self.no_of_maintenance = len(self.maintenance_ids.ids)

    owner_user_id = fields.Many2one('res.users', string='Created by', default=lambda s: s.env.uid)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', index=True)
    request_date = fields.Date('Request Date', track_visibility='onchange', default=fields.Date.context_today,
                           help="Date requested for the maintenance to happen")
    close_date = fields.Date('Close Date', help="Date the maintenance was finished.")
    maintenance_type = fields.Selection([('corrective', 'Corrective'), ('preventive', 'Preventive')], string='Maintenance Type', default="corrective")
    maintenance_team_id = fields.Many2one('maintenance.team', string='Team', required=True, default=_get_default_team_id)
    technician_user_id = fields.Many2one('res.users', string='Owner', track_visibility='onchange', oldname='user_id')
    schedule_date = fields.Datetime('Scheduled Date', help="Date the maintenance team plans the maintenance.  It should not differ much from the Request Date. ")
    duration = fields.Float(help="Duration in minutes and seconds.")
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    type_of_assets = fields.Selection([('fleet', 'Fleet'), ('other assets', 'Other Assets')], string="Type of Assets", default='fleet')
    asset_id = fields.Many2one('account.asset.asset', 'Asset')
    maintenance_ids = fields.One2many('maintenance.request', 'vehicle_id', copy=False)
    no_of_maintenance = fields.Integer('No Of Maintenance', compute='_get_no_maintenances')

    @api.multi
    def get_maintenances(self):
        action = self.env.ref('maintenance.hr_equipment_request_action').read()[0]
        action['domain'] = [('id', 'in', self.maintenance_ids.ids)]
        return action

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    asset_id = fields.Many2one('account.asset.asset', 'Asset')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    vehicle = fields.Boolean('Vehicle')
    equipment = fields.Boolean('Equipment')

    @api.multi
    @api.onchange('vehicle')
    def onchange_vehicle(self):
        if self.vehicle:
            self.equipment = False

    @api.multi
    @api.onchange('equipment')
    def onchange_equipment(self):
        if self.equipment:
            self.vehicle = False

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    asset_id = fields.Many2one('account.asset.asset', 'Asset')
    asset_category_id = fields.Many2one('account.asset.category', string='Equipment Category',
                                  track_visibility='onchange')
