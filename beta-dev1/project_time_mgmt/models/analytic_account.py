# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
from datetime import datetime

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    start_datetime = fields.Datetime('Start Date time', default=lambda self: fields.Datetime.now())
    end_datetime = fields.Datetime('End Date time', default=lambda self: fields.Datetime.now())
    unit_amount = fields.Float(compute='_get_duration', string='Duration', store=True)


    @api.one
    @api.depends('start_datetime', 'end_datetime')
    def _get_duration(self):
        """ Get the duration value between the 2 given dates. """
        start = self.start_datetime
        stop = self.end_datetime
        if start and stop:
            diff = fields.Datetime.from_string(stop) - fields.Datetime.from_string(start)
            if diff:
                self.unit_amount = round(float(diff.days) * 24 + (float(diff.seconds) / 3600), 2)
                return self.unit_amount
            return 0.0

    @api.one
    @api.constrains('start_datetime','end_datetime')
    def _check_days(self):
        if self.end_datetime <= self.start_datetime:
	    raise Warning(_('End date must be greater than start date'))
