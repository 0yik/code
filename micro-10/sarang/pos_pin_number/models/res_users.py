# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    pin_number = fields.Integer(string="PIN Number")

    _sql_constraints = [
        ('unique_pin', 'unique (pin_number)', 'The PIN NUmber must be unique!')
    ]
