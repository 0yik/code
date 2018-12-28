# -*- coding: utf-8 -*-

from odoo import models, fields, api

class team_configuration(models.Model):
    _name = 'team.configuration'

    name = fields.Char('Team Name', required=True)
    description = fields.Text('Description')
    working_schedule_id = fields.Many2one('resource.calendar', string='Working Schedule')
    employee_ids = fields.One2many('team.employee', 'team_id', 'Employee Lines')


    @api.multi
    def update_employee_working_schedule(self):
        for record in self:
            for employee in record.employee_ids:
                employee.employee_id.calendar_id = record.working_schedule_id

    @api.model
    def create(self, values):
        record = super(team_configuration, self).create(values)
        record.update_employee_working_schedule()
        return record

    @api.multi
    def write(self, values):
        result = super(team_configuration, self).write(values)
        self.update_employee_working_schedule()
        return result