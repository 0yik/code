# -*- coding: utf-8 -*-

from odoo import models, fields, api

class rating_config_inhrit(models.Model):
    _inherit = 'rating.config'

    rating_descrition = fields.Text(string='Rating Description')