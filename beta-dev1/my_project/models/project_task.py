# -*- coding: utf-8 -*-

from odoo import models, fields, api

class my_project_task(models.Model):
    _inherit = 'project.task'

    date_startdate = fields.Date('Start Date', default=lambda self: fields.Date.today())

    @api.multi
    def write(self, values):
        for record in self:
            if 'date_startdate' in values:
                forecasts = self.env['project.forecast'].search([('task_id', '=', record.id)])
                forecasts.write({
                    'start_date': values.get('date_startdate'),
                })
            if 'date_deadline' in values:
                forecasts = self.env['project.forecast'].search([('task_id', '=', record.id)])
                forecasts.write({
                    'end_date': values.get('date_deadline'),
                })
        return super(my_project_task, self).write(values)