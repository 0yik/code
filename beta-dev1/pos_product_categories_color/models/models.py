# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pos_category(models.Model):
    _inherit = 'pos.category'

    background_color = fields.Char('Background Color', default='#FFFFFF',)