# -*- coding: utf-8 -*-

from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    pos_access_minus = fields.Boolean(string='Access to Minus', default=True,
                                      help='Enabling this will allow user to minus POS')