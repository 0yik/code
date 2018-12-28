# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class trips_trips(models.Model):
    _name = 'trips.trips'

    vehicle_driver = fields.Many2one('res.users',  string='Driver')
    picking_id = fields.Many2one('stock.picking', string='Delivery Notes')
    picking_partner_id = fields.Many2one('res.partner', string='Partner')
    location_from_id = fields.Many2one('stock.location', 'Source Location')
    location_dest_id = fields.Many2one('stock.location', 'Destination Location')
    picking_date = fields.Datetime(string='Date')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

    @api.onchange('picking_id')
    def change_picking_id(self):
        if self.picking_id and self.picking_id.picking_type_id \
                and self.picking_id.picking_type_id.default_location_src_id:
            self.location_from_id = self.picking_id.picking_type_id.default_location_src_id.id
        elif self.picking_id and self.picking_id.location_id:
            self.location_from_id = self.picking_id.location_id.id
        else:
            self.location_from_id = False

        if self.picking_id and self.picking_id.picking_type_id \
                and self.picking_id.picking_type_id.default_location_dest_id:
            self.location_dest_id = self.picking_id.picking_type_id.default_location_dest_id.id
        elif self.picking_id and self.picking_id.location_dest_id:
            self.location_dest_id = self.picking_id.location_dest_id.id
        else:
            self.location_dest_id = False

        if self.picking_id and self.picking_id.partner_id:
            self.picking_partner_id = self.picking_id.partner_id.id
        else:
            self.picking_partner_id = False

        if self.picking_id and self.picking_id.min_date:
            self.picking_date = self.picking_id.min_date
        else:
            self.picking_date = False
