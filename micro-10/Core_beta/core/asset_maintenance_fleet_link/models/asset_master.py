# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AssetMaster(models.Model):
    _name = 'asset.master'
    _description = 'Asset Master'
    _inherit = 'mail.thread'
    _order = 'id desc'

    def _compute_count_all(self):
        for record in self:
            record.odometer_count = self.env['fleet.vehicle.odometer'].search_count([('vehicle_id', '=', record.fleet_id.id)])
            record.fuel_logs_count = self.env['fleet.vehicle.log.fuel'].search_count([('vehicle_id', '=', record.fleet_id.id)])
            record.service_count = self.env['fleet.vehicle.log.services'].search_count([('vehicle_id', '=', record.fleet_id.id)])
            record.contract_count = self.env['fleet.vehicle.log.contract'].search_count([('vehicle_id', '=', record.fleet_id.id)])
            record.cost_count = self.env['fleet.vehicle.cost'].search_count([('vehicle_id', '=', record.fleet_id.id), ('parent_id', '=', False)])
            if record.type == 'fleet':
                record.maintenance_count = len(record.fleet_id.maintenance_ids)
            else:
                record.maintenance_count = len(record.equipment_id.maintenance_ids)

    name = fields.Char('Name', required=True)
    asset_categ_id = fields.Many2one('account.asset.category', 'Category')
    type = fields.Selection([('fleet','Fleet'),('other assets','Other Assets')], 'Type of Asset')
    owner_id = fields.Many2one('res.users', 'Owner')
    location_id = fields.Many2one('stock.location', 'Location')
    company_id = fields.Many2one('res.company', 'Company')
    model_id = fields.Many2one('fleet.vehicle.model', 'Model')
    license_plate = fields.Char('License Plate')
    driver_id = fields.Many2one('res.partner', 'Driver')
    location = fields.Char('Location')
    vin_sn = fields.Char('Chassis Number')
    odometer = fields.Float('Last Odometer')
    odometer_unit = fields.Selection([('kilometers','Kilometers'),('miles','Miles')], 'Last Odometer', default='kilometers')
    acquisition_date = fields.Date('Acquisition Date')
    car_value = fields.Float('Car Value')
    seats = fields.Integer('Seats Number')
    doors = fields.Integer('Doors Number')
    color = fields.Char('Color')
    transmission = fields.Selection([(' manual','Manual'),('automatic','Automatic')], 'Transmission')
    fuel_type = fields.Selection([('gasoline','Gasoline'),('diesel','Diesel'),('electric','Electric'),('hybrid','Hybrid')], 'Fuel Type')
    co2 = fields.Float('CO2 Emissions')
    horsepower = fields.Integer('Horsepower')
    horsepower_tax = fields.Float('Horsepower Taxation')
    power = fields.Integer('Power')
    value = fields.Float('Value', required=True)
    asset_id = fields.Many2one('account.asset.asset', 'Asset', copy=False)
    fleet_id = fields.Many2one('fleet.vehicle', 'Fleet', copy=False)
    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', copy=False)
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('dispose','Disposed'),('cancel','Cancelled')], 'Status', track_visibility='onchange', default='draft')
    cost_count = fields.Integer(compute="_compute_count_all", string="Costs")
    contract_count = fields.Integer(compute="_compute_count_all", string='Contracts')
    service_count = fields.Integer(compute="_compute_count_all", string='Services')
    fuel_logs_count = fields.Integer(compute="_compute_count_all", string='Fuel Logs')
    odometer_count = fields.Integer(compute="_compute_count_all", string='Odometer')
    maintenance_count = fields.Integer(compute='_compute_count_all', string='Maintenance')

    @api.multi
    def button_confirm(self):
        self.ensure_one()
        vals = {}
        vals['name'] = self.name
        vals['category_id'] = self.asset_categ_id.id
        vals['owner_id'] = self.owner_id.id
        vals['date'] = fields.Date.today()
        vals['location'] = self.location
        vals['location_id'] = self.location_id.id
        vals['type_of_assets'] = self.type
        vals['licence_plate'] = self.license_plate
        vals['brand_id'] = self.model_id and self.model_id.brand_id.id
        vals['company_id'] = self.company_id.id or self.env.user.company_id.id
        vals['currency_id'] = self.env.user.company_id.currency_id.id
        vals['value'] = self.value
        vals['method'] = 'linear'
        vals['state'] = 'draft'
        vals['method_time'] = 'number'
        vals['method_number'] = self.asset_categ_id.method_number
        vals['method_period'] = self.asset_categ_id.method_period
        asset = self.env['account.asset.asset'].create(vals)
#         asset.validate()
        asset.create_asset_tracking()
        # Update fleet values
        fleet_id = False
        equipment_id = False
        if self.type == 'fleet':
            fleet_id = self.env['fleet.vehicle'].search([('asset_id','=',asset.id)])
            print "1111111111<<<<<<<<!111111111111",fleet_id
            vals = {}
            vals['driver_id'] = self.owner_id.id
            vals['vin_sn'] = self.vin_sn
            vals['location'] = self.location_id.id
            vals['odometer'] = self.odometer
            vals['odometer_unit'] = self.odometer_unit
            vals['acquisition_date'] = self.acquisition_date
            vals['car_value'] = self.value
            vals['seats'] = self.seats
            vals['doors'] = self.doors
            vals['color'] = self.color
            vals['transmission'] = self.transmission
            vals['fuel_type'] = self.fuel_type
            vals['fuel_type'] = self.fuel_type
            vals['co2'] = self.co2
            vals['horsepower'] = self.horsepower
            vals['horsepower_tax'] = self.horsepower_tax
            vals['power'] = self.power
            fleet_id.write(vals)
        elif self.type == 'other assets':
            equipment_id = self.env['maintenance.equipment'].search([('asset_id', '=', asset.id)])
        self.write({'state': 'confirm', 'asset_id': asset.id, 'fleet_id': fleet_id and fleet_id.id, 'equipment_id': equipment_id and equipment_id.id})

    @api.multi
    def button_dispose(self):
        return {
            'name': 'Sell / Dispose Asset Wizard',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'journal.creation.wizard',
            'target': 'new',
            'context': {'asset_master_id': self.id, 'asset_id': self.asset_id.id},
        }

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_open_asset(self):
        self.ensure_one()
        action = self.env.ref('account_asset.action_account_asset_asset_form').read()[0]
        action['domain'] = [('id','=',self.asset_id.id)]
        return action

    @api.multi
    def action_open_fleet(self):
        self.ensure_one()
        action = self.env.ref('fleet.fleet_vehicle_action').read()[0]
        action['domain'] = [('id','=',self.fleet_id.id)]
        return action

    @api.multi
    def action_open_equipment(self):
        self.ensure_one()
        action = self.env.ref('maintenance.hr_equipment_action').read()[0]
        action['domain'] = [('id','=',self.equipment_id.id)]
        return action

    @api.multi
    def return_action_to_open(self):
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('fleet', xml_id)
            res.update(context=dict(self.env.context, default_vehicle_id=self.id, group_by=False), domain=[('vehicle_id', '=', self.fleet_id.id)])
            return res
        return False

    @api.multi
    def act_show_log_cost(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('fleet', 'fleet_vehicle_costs_action')
        res.update(context=dict(self.env.context, default_vehicle_id=self.id, search_default_parent_false=True), domain=[('vehicle_id', '=', self.fleet_id.id)])
        return res

    @api.multi
    def get_maintenances(self):
        if self.type == 'fleet':
            action = self.env.ref('maintenance.hr_equipment_request_action').read()[0]
            action['domain'] = [('vehicle_id', '=', self.fleet_id.id)]
        else:
            action = self.env.ref('maintenance.hr_equipment_request_action').read()[0]
            action['domain'] = [('equipment_id', '=', self.equipment_id.id)]
        return action

AssetMaster()