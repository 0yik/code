# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    sequence = fields.Integer('Sequence')