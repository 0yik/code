from odoo import api, fields, models, _
import json
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class pos_config(models.Model):
    _inherit = "pos.config"

    screen_type = fields.Selection(selection_add=[
        ('takeaway', 'Take Away'),
    ],  string='Session Type', default='waiter')

    category_takeaway_lines = fields.One2many('category.mapping.line', 'config_id3',)

class CategoryMappingLine(models.Model):
    _inherit = 'category.mapping.line'

    config_id3 = fields.Many2one('pos.config')
