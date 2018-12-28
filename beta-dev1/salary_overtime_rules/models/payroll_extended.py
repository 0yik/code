# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today MpTechnolabs.
#    (<http://serpentcs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import math
import calendar
import odoo.tools as tools
import odoo.tools.safe_eval
from dateutil import parser, rrule
from datetime import date, datetime, timedelta
from odoo import fields, api, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    @api.depends('date_from', 'date_to','employee_id','employee_id.user_id')
    def _get_total_public_holiday_hours(self):
        res = {}
        for payslip in self:
            public_holi_ids = self.env['hr.holiday.lines'].search([('holiday_date', '>=', payslip.date_from),
                                                                   ('holiday_date', '<=', payslip.date_to),
                                                                   ('holiday_id.state', '=', 'validated')])
            pub_holi_days = []
            for line in public_holi_ids:
                pub_holi_days.append(line.holiday_date)
            total_hours = 0.0
            public_holiday_hours = 0.0
            weekend_hours = 0.0
            if payslip.employee_id.user_id:
                account_analytic_search_ids = self.env['account.analytic.line'].search([('user_id', '=', payslip.employee_id.user_id.id), 
                                                                                        ('date', '>=', payslip.date_from),
                                                                                        ('date', '<=', payslip.date_to),
                                                                                        ('date', 'in', pub_holi_days)])
                if account_analytic_search_ids and account_analytic_search_ids.ids:
                    for timesheet in account_analytic_search_ids:
                        public_holiday_hours = public_holiday_hours + timesheet.unit_amount or 0.0
                day_from = datetime.strptime(payslip.date_from,"%Y-%m-%d")
                day_to = datetime.strptime(payslip.date_to,"%Y-%m-%d")
                nb_of_days = (day_to - day_from).days + 1
                for day in range(0, nb_of_days):
                    account_analytic_search_ids = self.env['account.analytic.line'].search([('user_id', '=', payslip.employee_id.user_id.id), 
                                                                                            ('date', '=', day_from + timedelta(days=day))])
                    for timesheet in account_analytic_search_ids:
                        working_hours_on_day = payslip.contract_id.working_hours.working_hours_on_day(day_from + timedelta(days=day))
                        if working_hours_on_day==0 and timesheet.unit_amount>0:
                            weekend_hours = weekend_hours + timesheet.unit_amount or 0.0
                total_hours = weekend_hours + public_holiday_hours
                self.pub_holiday_hours = total_hours

    @api.multi
    @api.depends('employee_id.user_id', 'date_from', 'date_to','employee_id')
    def _get_total_hours(self):
        for payslip in self:
            total_timesheet_hours = 0.0
            overtime_hours = 0.0
            if payslip.employee_id.user_id:
                day_from = datetime.strptime(payslip.date_from,"%Y-%m-%d")
                day_to = datetime.strptime(payslip.date_to,"%Y-%m-%d")
                nb_of_days = (day_to - day_from).days + 1
                for day in range(0, nb_of_days):
                    account_analytic_search_ids = self.env['account.analytic.line'].search([('user_id', '=', payslip.employee_id.user_id.id), 
                                                                                            ('date', '=', day_from + timedelta(days=day))])
                    for timesheet in account_analytic_search_ids:
                        working_hours_on_day = payslip.contract_id.working_hours.working_hours_on_day(day_from + timedelta(days=day))
                        if working_hours_on_day and timesheet.unit_amount > working_hours_on_day:
                            overtime_hours = overtime_hours + (timesheet.unit_amount - working_hours_on_day)
                payslip.overtime_hours = overtime_hours
                account_analytic_search_ids = self.env['account.analytic.line'].search([('user_id', '=', payslip.employee_id.user_id.id), 
                                                                                        ('date', '>=', payslip.date_from),
                                                                                        ('date', '<=', payslip.date_to)])
                for timesheet in account_analytic_search_ids:
                    total_timesheet_hours = total_timesheet_hours + timesheet.unit_amount or 0.0
                    self.total_timesheet_hours = total_timesheet_hours
            self.total_hours = 0.0
            for work_days in payslip.worked_days_line_ids:
                if work_days.code == 'WORK100':
                    self.total_hours = work_days.number_of_hours

    total_timesheet_hours = fields.Float(compute = '_get_total_hours', string='Total Timesheet Hours')
    total_hours = fields.Float(compute = '_get_total_hours', string='Total Hours')
    overtime_hours = fields.Float(compute = '_get_total_hours', string='Overtime Hours')
    pub_holiday_hours = fields.Float(compute = '_get_total_public_holiday_hours', string='Public Holiday Hours')
