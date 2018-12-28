# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    receipt_symbol = fields.Boolean(string='Show symbol on receipt')