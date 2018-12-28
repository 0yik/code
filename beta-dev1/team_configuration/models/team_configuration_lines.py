# -*- coding: utf-8 -*-

from odoo import models, fields, api

class team_configuration_lines(models.Model):
    _name='team_configuration_lines'

    team_configuration_id = fields.Many2one('team.configuration')
    employee_id = fields.Many2one('hr.employee', string="Employee")