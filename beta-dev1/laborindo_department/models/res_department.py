# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResDepartment(models.Model):
    _name = 'res.department'

    name = fields.Char('Name')

