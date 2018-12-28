from odoo import models, fields

class custom_stock_config_settings(models.TransientModel):
    _inherit = 'stock.config.settings'

    lot_or_serial_no = fields.Selection(string="Lot no/ Serial no.",
                                        selection=[('lot', 'LOT'), ('serial_no', 'Serial Number')],
                                        help='This allows you to assign lot no. or slit and assign serial no.',
                                        default="lot")

custom_stock_config_settings()