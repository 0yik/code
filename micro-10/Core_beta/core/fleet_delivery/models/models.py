# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    driver_id = fields.Many2one('res.users', string='Driver')
    trips_count = fields.Integer("Trips", compute='_compute_trips_count')

    @api.multi
    def _compute_trips_count(self):
        for one_vehicle in self:
            one_vehicle.trips_count = self.env['trips.trips'].search_count(
                [('vehicle_id', '=', one_vehicle.id)])

    @api.multi
    def action_view_delivery_order(self):
        # domain = self.search([('vehicle_id','=',self.vehicle_id.id)]).ids
        return {
            'name': _('Stock Operations'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('vehicle_id', '=', self.id)],
            # 'context': context,
        }

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    vehicle_driver = fields.Many2one('res.users', string='Driver')

    @api.onchange('vehicle_id')
    def change_vehicle_id(self):
        if self.vehicle_id and self.vehicle_id.driver_id:
            self.vehicle_driver = self.vehicle_id.driver_id.id
        else:
            self.vehicle_driver = False

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals and vals.get('date_done'):
                self.env['trips.trips'].sudo().create({
                    'vehicle_driver': rec.vehicle_driver and rec.vehicle_driver.id or False,
                    'picking_id': rec.id,
                    'picking_partner_id': rec.partner_id and rec.partner_id.id or False,
                    'location_from_id': (rec.picking_type_id and \
                                        rec.picking_type_id.default_location_src_id and \
                                        rec.picking_type_id.default_location_src_id.id) or \
                                        (rec.location_id and rec.location_id.id) or False,
                    'location_dest_id': (rec.picking_type_id and \
                                        rec.picking_type_id.default_location_dest_id and \
                                        rec.picking_type_id.default_location_dest_id.id) or
                                        (rec.location_dest_id and rec.location_dest_id.id) or False,
                    'picking_date': rec.min_date or False,
                    'vehicle_id': rec.vehicle_id and rec.vehicle_id.id or False,
                })
        return super(stock_picking, self).write(vals)

