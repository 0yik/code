# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class MyUsers(models.Model):

    _inherit = 'res.users'

    color = fields.Selection([
        ('0', '#FFFFFF'),
        ('1', '#d8d8d8'),
        ('2', '#e5d8e3'),
        ('3', '#ece9c2'),
        ('4', '#dee180'),
        ('5', '#abd4cc'),
        ('6', '#b8e3e8'),
        ('7', '#f4ddab'),
        ('8', '#7f637d'),
        ('9', '#d8c5d5'),
    ], string='Color Index', default=0)

    # color = fields.Integer(string='Color Index', default=0)
