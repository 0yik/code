# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class PosConfig(models.Model):
#     _inherit = 'pos.config'
#
#     discount_amount = fields.Char(string='Discount Amount')
class pos_promotion(models.Model):
    _inherit = 'pos.promotion'

    pos_configs = fields.Many2many('pos.config','pos_config_promotion_rel','promotion_id','config_id',string='Assigned to POS')

