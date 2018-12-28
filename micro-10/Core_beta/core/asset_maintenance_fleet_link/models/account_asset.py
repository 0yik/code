# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAssets(models.Model):
    _inherit = 'account.asset.asset'

    @api.multi
    def _get_no_equipments(self):
        if self.equipment_ids:
            self.no_of_equipments = len(self.equipment_ids.ids)

    location_id = fields.Many2one('stock.location', string='Location')
    type_of_assets = fields.Selection([('fleet', 'Fleet'), ('other assets', 'Other Assets')], string="Type of Assets")
    licence_plate = fields.Char(string="Licence Plate")
    brand_id = fields.Many2one('fleet.vehicle.model.brand', 'Brand')
    maintenance_ids = fields.One2many('maintenance.request', 'asset_id', copy=False)
    equipment_ids = fields.One2many('maintenance.equipment', 'asset_id', copy=False)
    fleet_ids = fields.One2many('fleet.vehicle', 'asset_id', copy=False)
    no_of_equipments = fields.Integer('No Of Equipments', compute='_get_no_equipments')

    @api.multi
    def get_equipment(self):
        action = self.env.ref('maintenance.hr_equipment_action').read()[0]
        action['domain'] = [('id', 'in', self.equipment_ids.ids)]
        return action


    @api.multi
    def create_asset_tracking(self):
        if self.type_of_assets == 'fleet':
            vehicle_model_obj = self.env['fleet.vehicle.model'].search([('name', '=', self.name)])
            if not vehicle_model_obj:
                vehicle_model = self.env['fleet.vehicle.model'].create({'name': self.name, 'brand_id': self.brand_id.id})
            else:
                vehicle_model = vehicle_model_obj
            vals = {
                'model_id': vehicle_model.id,
                'license_plate': self.licence_plate,
                'type_of_assets': 'fleet',
                'asset_id': self.id,
                'location': self.location_id.name,
            }
            fleet_obj = self.env['fleet.vehicle'].create(vals)
            action = self.env.ref('fleet.fleet_vehicle_action').read()[0]
            action['res_id'] = fleet_obj.id
            action['domain']= [('id', '=', fleet_obj.id)]
            action['views'] = [(self.env.ref('fleet.fleet_vehicle_view_form').id, 'form')]
            return action
        if self.type_of_assets == 'other assets':
            equipment_obj = self.env['maintenance.equipment'].create({'name': self.name, 'asset_id':self.id, 'location': self.location_id.name, 'owner_user_id': self.owner_id.id, 'asset_category_id': self.category_id.id})
            action = self.env.ref('maintenance.hr_equipment_action').read()[0]
            action['res_id'] = equipment_obj.id
            action['domain'] = [('id', '=', equipment_obj.id)]
            action['views'] = [(self.env.ref('maintenance.hr_equipment_view_form').id, 'form')]
            return action
