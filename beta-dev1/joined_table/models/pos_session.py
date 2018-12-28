# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _

class PosSession(models.Model):
    _inherit = 'pos.session'
    _order = 'id desc'

    sequence_alphabet = fields.Char(string='Order Sequence', help='A sequence number that is incremented with each order', default='A')

