from odoo import api, models, fields, registry
import logging

_logger = logging.getLogger(__name__)

class pos_bus(models.Model):
    _name = "pos.bus"

    name = fields.Char('Name', required=1)
    orders_store = fields.Text('Cache data')

    @api.model
    def get_cache_order(self, bus_id):
        bus = self.sudo().search([('id', '=', bus_id)])
        if bus and bus[0].orders_store:
            return eval(bus[0].orders_store)
        else:
            return {}


class pos_config(models.Model):
    _inherit = 'pos.config'

    bus_id = fields.Many2one('pos.bus', string='Shop (bus) location')
    user_ids = fields.Many2many('res.users', string='Assigned to')
    display_person_add_line = fields.Boolean('Display Infor', default=1,
                                             help="When you checked, on pos order lines screen, will display information person created order (lines) Eg: create date, updated date ..")
