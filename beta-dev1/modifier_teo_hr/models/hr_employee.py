from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def compute_months_in_service(self):
        for emp in self:
            months_in_service = 0
            if emp.join_date:
                join_date = fields.Date.from_string(emp.join_date)
                end_date = date.today()
                if emp.emp_status in ['in_notice', 'terminated']:
                    end_date = fields.Date.from_string(emp.cessation_date)
                diff = relativedelta(end_date, join_date)
                months_in_service = (diff.years * 12) + diff.months
            emp.months_in_service = months_in_service

    months_in_service = fields.Integer(compute='compute_months_in_service', string='Months in Service')


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.multi
    def name_get(self):
        res = []
        for leave in self:
            res.append((leave.id, _("%s") % leave.employee_id.name))
        return res

    allday = fields.Boolean("All Day", default=True)
    leave_code = fields.Char(related='holiday_status_id.name', string='Leave Code', store=True, readonly=True)
