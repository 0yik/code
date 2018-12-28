from odoo import api, fields, models, _
from odoo.exceptions import UserError

class pos_config(models.Model):

    _inherit = "pos.config"

    auto_create_delivery_order = fields.Boolean('Create delivery order')
    picking_state = fields.Selection([
        ('action_confirm', 'Confirm'),
        ('force_assign', 'Force Assign'),
        ('do_transfer', 'Do Transfer'),
    ], 'Picking state', default='action_confirm', help='State of Delivery order will process to')

