# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class resource_calendar(models.Model):
    _inherit = 'resource.calendar'

    start_cycle_date = fields.Date('Start Cycle Date')

    @api.multi
    def get_attendances_for_weekday(self, day_dt):
        """ Given a day datetime, return matching attendances """
        self.ensure_one()
        attendances = self.env['resource.calendar.attendance']
        if self.start_cycle_date:
            number_date = self.get_number_day_sequence(day_dt)
            if number_date:
                for attendance in self.attendance_ids.filtered(
                        lambda att: not att.off_day and att.day_seq == number_date):
                    attendances += attendance
        return attendances

    @api.model
    def get_number_day_sequence(self, day_dt):
        if self.start_cycle_date:
            start_cc = fields.Datetime.from_string(self.start_cycle_date)
            cc_len = self.get_cycle_len()
            if day_dt.date() >= start_cc.date() and cc_len:
                days = day_dt.date() - start_cc.date()
                number_day = (days.days % cc_len) + 1
                return number_day
        return False

    @api.model
    def get_cycle_len(self):
        attendances = self.attendance_ids.filtered(lambda r: r.off_day == False)
        seq_number = set(attendances.mapped('day_seq'))
        if len(seq_number) > 0:
            cc_len = (max(seq_number) - min(seq_number)) + 1
            return cc_len
        return False