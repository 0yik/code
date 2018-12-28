# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class VehicleConfig(models.Model):
    _name = 'vehicle.config'
    _description = 'Vehicle Configuration'

    vehicle_id = fields.Many2one(
        comodel_name='product.product', string='Vehicle Number',
        help='Add Vehicle', domain=[('is_equipment', '=', True)])
    team_id = fields.Many2one(
        comodel_name='booking.team',
        string='Team Name', help='Add team for the vehicle')
    vehicle_service_line_ids = fields.One2many(
        comodel_name='vehicle.line.service',
        inverse_name='vehicle_config_id',
        string='Service Type', help='Service Type')
    vehicle_product_ids = fields.One2many(
        comodel_name='vehicle.prod.line',
        inverse_name='vehicle_config_id',
        string='Product', help='Add product for vehicle')


VehicleConfig()


class VehicleLine(models.Model):
    _name = 'vehicle.line.service'
    _description = 'Vehicle Line'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Service Type', help='Service Type',
        domain=[('type', '=', 'service')]
    )
    vehicle_config_id = fields.Many2one(
        comodel_name='vehicle.config', string='Vehicl Config Ref',
        help='Reference of vehicle config.', )


VehicleLine()


class Vehicle_Prod_Line(models.Model):
    _name = 'vehicle.prod.line'
    _description = 'Vehicle Products'

    vehicle_prod_id = fields.Many2one(
        comodel_name='product.product',
        string='Product', help='Add product of vehicle',
    )
    vehicle_config_id = fields.Many2one(
        comodel_name='vehicle.config', string='Vehicl Config Ref',
        help='Reference of vehicle config.', )


Vehicle_Prod_Line()



