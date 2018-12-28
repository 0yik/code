from odoo import api, fields, models

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    seat_no = fields.Integer('Seat Number')

PosOrderLine()