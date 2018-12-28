# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pos_config(models.Model):
    _inherit = 'pos.config'

    charge = fields.Float(related="branch_id.servicecharge", store=True,help='this field is used to take service charge percentage from branch')

    