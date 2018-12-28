from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    header_logo = fields.Binary(string='Header Logo')
    height_logo = fields.Integer(string='Height Logo', help='Height of the header logo in pixels')
    width_logo = fields.Integer(string='Width Logo', help='Width of the header logo in pixels')