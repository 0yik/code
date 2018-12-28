# -*- coding: utf-8 -*-
from datetime import date, datetime, time, timedelta
from odoo import models, fields, api

class my_project_forecast(models.Model):
    _inherit = 'project.forecast'

    def default_end_date(self):
        return date.today() + timedelta(days=1)

    start_date = fields.Date(compute='_compute_date', store=True, readonly=False)
    end_date = fields.Date(compute='_compute_date', store=True, readonly=False)

    @api.multi
    def _compute_date(self):
        for record in self:
            if record.task_id:
                record.start_date = record.task_id.date_startdate
                record.end_date = record.task_id.date_deadline

    @api.model
    def create(self, values):
        result = super(my_project_forecast, self).create(values)
        return result