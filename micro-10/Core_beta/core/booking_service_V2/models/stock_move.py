# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError, Warning

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    location_dest_id = fields.Many2one(
    'stock.location', 'Destination Location',
    auto_join=True, index=True, required=False, states={'done': [('readonly', True)]},
    help="Location where the system will stock the finished products.")
