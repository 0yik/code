# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosConfig(models.Model):
    
    _inherit = "pos.config"

    number_1 = fields.Char('1', required=True, default='Y')
    number_2 = fields.Char('2', required=True, default='A')
    number_3 = fields.Char('3', required=True, default='I')
    number_4 = fields.Char('4', required=True, default='K')
    number_5 = fields.Char('5', required=True, default='C')
    number_6 = fields.Char('6', required=True, default='H')
    number_7 = fields.Char('7', required=True, default='N')
    number_8 = fields.Char('8', required=True, default='M')
    number_9 = fields.Char('9', required=True, default='E')
    number_0 = fields.Char('0', required=True, default='R')
    number_dot = fields.Char('.', required=True, default='O')

    