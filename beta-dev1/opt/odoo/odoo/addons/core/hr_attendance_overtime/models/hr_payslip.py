# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil import rrule, parser
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    @api.depends('ot_date_from', 'ot_date_to', 'employee_id')
    def _compute_hours(self):
        for rec in self:
            ot1_hours = 0.00
            ot1_5_hours = 0.00
            ot2_hours = 0.00
            if rec.employee_id and rec.ot_date_from and rec.ot_date_to:
                dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(rec.ot_date_from),
                                         until=parser.parse(rec.ot_date_to)))
                for date_line in dates:
                    emp_attendance = self.env['hr_timesheet_sheet.sheet.day'].sudo().search(
                        [('name','=',date_line), ('sheet_id.employee_id', '=', rec.employee_id.id)])
                    if emp_attendance:
                        ot1_hours += emp_attendance.ot1_hours
                        ot1_5_hours += emp_attendance.ot1_5_hours
                        ot2_hours += emp_attendance.ot2_hours

            rec.ot1_hours = ot1_hours
            rec.ot1_5_hours = ot1_5_hours
            rec.ot2_hours = ot2_hours

    ot1_hours = fields.Float('OT 1.0 Hours', compute='_compute_hours', help="Employee works on public holidays.")
    ot1_5_hours = fields.Float('OT 1.5 Hours', compute='_compute_hours', help="Employee works overtime on normal working days.")
    ot2_hours = fields.Float('OT 2.0 Hours', compute='_compute_hours', help="Total overtime hours on weekend.")
