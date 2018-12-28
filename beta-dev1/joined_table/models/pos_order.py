# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _


class PosOrder(models.Model):
    _inherit = "pos.order"
    _description = "Point of Sale Orders"
    _order = "id desc"


    sequence_alphabet = fields.Char(string='Order Sequence', help='A sequence number that is incremented with each order', default='A')

