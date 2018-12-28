
from odoo import fields, api, models

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    customer_note_name = fields.Char('Customer Note Name')