# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class resource_calendar_attendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    off_day = fields.Boolean('Off Day')
    day_seq = fields.Integer('Day Number', required=True, help='Start Cycle with 1')

    @api.one
    @api.constrains('day_seq')
    def _check_description(self):
        if self.day_seq < 1:
            raise ValidationError("Day Number should be greater or equal than 1")
