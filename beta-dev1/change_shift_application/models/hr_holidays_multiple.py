# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError

HOURS_PER_DAY = 8


class hr_holidays_multiple(models.Model):
    _inherit = "hr.holidays.multiple"

    @api.multi
    def action_approve(self):
        res = super(hr_holidays_multiple, self).action_approve()
        self.compute_for_change_shift()
        return res

    @api.multi
    def compute_for_change_shift(self):
        type = self.env.ref('change_shift_application.change_shift_type')
        for holiday in self:
            if holiday.state == 'validate' and holiday.holiday_status_id and holiday.holiday_status_id.id == type.id:
                for holiday_line in holiday.holiday_line_ids.filtered(
                        lambda r: r.holiday_status_id.id == type.id and r.state == 'validate'):
                    holiday_line.create_change_shift_interval()
        return
