from odoo import models, fields, api,_


class sale_order(models.Model):
    _name = 'vehicle.number'
    _rec_name = 'number'

    number = fields.Char('Vechicle Number')
    name = fields.Char(string='Vechicle Name')


class stock_picking_wave(models.Model):
    _inherit = 'stock.picking.wave'

    vehicle_number_id = fields.Many2one('vehicle.number','Vechicle Number')
