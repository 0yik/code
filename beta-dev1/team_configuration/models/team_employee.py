# -*- coding: utf-8 -*-

from odoo import models, fields, api

class team_employee(models.Model):
    _name = 'team.employee'

    team_id = fields.Many2one('team.configuration')
    employee_id = fields.Many2one('hr.employee', required=True)