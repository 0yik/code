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
import pytz
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    def was_on_leave(self,employee_id, datetime_day):
        res1 = {'name':False, 'days':0.0,'half_work':False}
        day = datetime_day.strftime("%Y-%m-%d")
        holiday_ids = self.env['hr.holidays'].search([('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
        if holiday_ids:
            res = holiday_ids[0].holiday_status_id.name
            res1['name'] = res
            num_days = 1.0
            if holiday_ids[0].half_day == True:
                num_days = 0.5
                res1['half_work'] = True
            res1['days'] = num_days
        return res1

    @api.multi
    @api.depends('date_from', 'date_to','employee_id','employee_id.user_id')
    def _get_total_absence_days(self):
        for payslip in self:
            public_holi_ids = self.env['hr.holiday.lines'].search([('holiday_date', '>=', payslip.date_from),
                                                                   ('holiday_date', '<=', payslip.date_to),
                                                                   ('holiday_id.state', '=', 'validated')])
            pub_holi_days = []
            for line in public_holi_ids:
                pub_holi_days.append(line.holiday_date)
            total_days = 0.0
            day_from = datetime.strptime(payslip.date_from,"%Y-%m-%d")
            day_to = datetime.strptime(payslip.date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', payslip.employee_id.id), 
                                                                   ('check_in', '>=', str((day_from + timedelta(days=day)).date())),
                                                                   ('check_in', '<=', str((day_from + timedelta(days=day)).date()))])
                leave = self.was_on_leave(payslip.employee_id.id, day_from + timedelta(days=day))
                if leave.get('days') == 0 and not attendance_ids:
                    working_hours_on_day = payslip.contract_id.working_hours.working_hours_on_day(day_from + timedelta(days=day))
                    if working_hours_on_day > 0 and str((day_from + timedelta(days=day)).date()) not in pub_holi_days:
                        total_days = total_days + 1
            self.total_absence_days = total_days
            work_day = self.env['hr.payslip.worked_days'].search([('payslip_id','=',payslip.id),('code','=','WORK100')])
            for work in work_day:
                if work.number_of_days>0:
                    one_day = (payslip.contract_id.wage / work.number_of_days)
                    if one_day > 0:
                        self.absence_deduction = (one_day * payslip.total_absence_days)
            abs_config = self.env['hr.employee.config.settings'].search([])
            if abs_config:
                last_record = self.env['hr.employee.config.settings'].browse(max(abs_config.ids))
                if last_record.absence_fee_type=='fixed':
                    self.absence_deduction = (last_record.absence_fee_deduction * payslip.total_absence_days)
    
    @api.multi
    @api.depends('date_from', 'date_to','employee_id','employee_id.user_id')
    def _get_late_enrty_count(self):
        for payslip in self:
            total_late_entry = 0.0
            resorce_cal_attendance_obj = self.env['resource.calendar.attendance']
            emp_config = self.env['hr.employee.config.settings'].search([])
            last_record = False
            if emp_config:
                last_record = self.env['hr.employee.config.settings'].browse(max(emp_config.ids))
            day_from = datetime.strptime(payslip.date_from,"%Y-%m-%d")
            day_to = datetime.strptime(payslip.date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                resorce_cal_attendance = resorce_cal_attendance_obj.search([('dayofweek','=',(day_from + timedelta(days=day)).weekday()),('calendar_id','=',payslip.contract_id.working_hours.id)])
                attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', payslip.employee_id.id),
                                                                   ('check_in', '>=', str((day_from + timedelta(days=day)).date())),
                                                                   ('check_in', '<=', str((day_from + timedelta(days=day)).date()))])
                for attendance in attendance_ids:
                    tz = pytz.timezone(self.env.user.partner_id.tz) or pytz.utc
                    check_in = pytz.utc.localize(datetime.strptime(attendance.check_in, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
                    allowed_hours = resorce_cal_attendance and resorce_cal_attendance[0].hour_from or 0
                    if last_record and last_record.late_minutes_buffer > 0:
                        allowed_mins = last_record.late_minutes_buffer + ((resorce_cal_attendance and resorce_cal_attendance[0].hour_from or 0) * 60 )
                        hours, minutes = divmod(allowed_mins, 60)
                        min_time = "%02d:%02d"%(hours,minutes)
                        if str(check_in.time()) > min_time:
                            total_late_entry = total_late_entry + 1
            payslip.late_entry_count = total_late_entry
            if last_record and last_record.late_entry_deduction>0:
                payslip.late_entry_deduction = (last_record.late_entry_deduction * payslip.late_entry_count)
            else:
                payslip.late_entry_deduction = 0

    total_absence_days = fields.Float(compute = '_get_total_absence_days', string='Total Absence Days')
    absence_deduction = fields.Float(compute = '_get_total_absence_days', string='Absence Deduction')
    late_entry_count = fields.Integer(compute = '_get_late_enrty_count',string='Late Entry Count')
    late_entry_deduction = fields.Float(compute = '_get_late_enrty_count', string='Late Entry Deduction')
