# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from dateutil import rrule, parser
import logging
_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, \
DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError


class hr_holiday_lines_inherit(models.Model):
    _inherit = 'hr.holiday.lines'

    state = fields.Selection(related='holiday_id.state', string='Status', store=True)

class HrTimesheetIN(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    # period_ids = fields.One2many('hr_timesheet_sheet.sheet.day', 'sheet_id', string='Period')
    ts_period_ids = fields.One2many('hr_timesheet_sheet.sheet.periods', 'sheet_id', string='Period')

    @api.model
    def count_public_holiday_ex(self, date_from, period):
        public_holidays = []
        models = self.env['ir.model'].search([('model', '=', 'hr.holidays.public.line')])
        if models:
            holiday_obj = self.env['hr.holidays.public.line']
            public_holidays = holiday_obj.search([('date', '=', date_from)])
        return public_holidays

    @api.multi
    def count_leaves_ex(self, date_from, employee_id, period):
        holiday_obj = self.env['hr.holidays']
        start_leave_period = end_leave_period = False
        if period.get('date_from') and period.get('date_to'):
            start_leave_period = period.get('date_from')
            end_leave_period = period.get('date_to')
        holiday_ids = holiday_obj.search(
            ['|', '&', ('date_from', '>=', start_leave_period), ('date_from', '<=', end_leave_period),
             '&', ('date_to', '<=', end_leave_period), ('date_to', '>=', start_leave_period),
             ('employee_id', '=', employee_id), ('state', '=', 'validate'), ('type', '=', 'remove')])
        leaves = []
        for leave in holiday_ids:
            leave_date_from = datetime.strptime(leave.date_from, '%Y-%m-%d %H:%M:%S')
            leave_date_to = datetime.strptime(leave.date_to, '%Y-%m-%d %H:%M:%S')
            leave_dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(leave.date_from),
                                           until=parser.parse(leave.date_to)))
            for date in leave_dates:
                if date.strftime('%Y-%m-%d') == date_from.strftime('%Y-%m-%d'):
                    leaves.append((leave_date_from, leave_date_to, leave.number_of_days))
                    break
        return leaves

    @api.multi
    def calculate_duty_hours_ex(self, date_from, period):
        contract_obj = self.env['hr.contract']
        duty_hours = 0.0
        contract_ids = contract_obj.search(
            [('employee_id', '=', self.employee_id.id), ('date_start', '<=', date_from),
                '|', ('date_end', '>=', date_from), ('date_end', '=', None)
            ])
        for contract in contract_ids:
            ctx = dict(self.env.context).copy()
            ctx.update(period)
            dh = contract.working_hours.get_working_hours_of_date(
                start_dt=date_from,
                resource_id=self.employee_id.id)
            leaves = self.count_leaves_ex(date_from, self.employee_id.id, period)
            public_holiday = self.count_public_holiday_ex(date_from, period)
            if not leaves and not public_holiday:
                if not dh:
                    dh = 0.00
                duty_hours += dh
            elif not leaves and public_holiday:
                dh = 0.00
                duty_hours += dh
            else:
                if leaves[-1] and leaves[-1][-1]:
                    if float(leaves[-1][-1]) == (-0.5):
                        duty_hours += dh / 2
        return duty_hours

class HrTimesheetSH(models.Model):
    _name = 'hr_timesheet_sheet.sheet.periods'

    @api.onchange('date')
    def onchange_date(self):
        ot1_hours = 0.00
        ot1_5_hours = 0.00
        ot2_hours = 0.00
        if self.sheet_id and self.sheet_id.employee_id and self.date:
            emp_attendance = self.env['hr_timesheet_sheet.sheet.day'].sudo().search(
                [('name', '=', self.date), ('sheet_id.employee_id', '=', self.sheet_id.employee_id.id)])
            if emp_attendance:
                ot1_hours += emp_attendance.ot1_hours
                ot1_5_hours += emp_attendance.ot1_5_hours
                ot2_hours += emp_attendance.ot2_hours

        self.ot1_hours_manager = ot1_hours
        self.ot1_5_hours_manager = ot1_5_hours
        self.ot2_hours_manager = ot2_hours

    sheet_id = fields.Many2one('hr_timesheet_sheet.sheet', string='Sheet')
    date = fields.Date(string='Date')
    ot1_hours_manager = fields.Float(string='OT 1.0 (Manager)')
    ot1_5_hours_manager = fields.Float(string='OT 1.5 (Manager)')
    ot2_hours_manager = fields.Float(string='OT 2.0 (Manager)')
    manager_remarks = fields.Text(string='Manager Remarks')

    @api.multi
    def check_date(self):
        for one_period in self:
            if one_period.date and one_period.sheet_id:
                check_periods = self.env['hr_timesheet_sheet.sheet.periods'].sudo().search(
                    [('sheet_id', '=', one_period.sheet_id.id),('date', '=', one_period.date)])
                if len(check_periods) > 1:
                    raise ValidationError(_('You can not select same date in "Timesheet Comments by Manager"!'))
            if one_period.date and one_period.sheet_id and one_period.sheet_id.date_from and one_period.sheet_id.date_to:
                if one_period.date < one_period.sheet_id.date_from or one_period.date > one_period.sheet_id.date_to:
                    raise ValidationError(_('Please select date between Timesheet Period!'))

    @api.model
    def create(self, vals):
        res = super(HrTimesheetSH, self).create(vals)
        res.check_date()
        return res

    @api.multi
    def write(self, vals):
        res = super(HrTimesheetSH, self).write(vals)
        self.check_date()
        return res


class hrattendance(models.Model):
    _inherit = "hr.attendance"

    @api.model
    def get_diff1(self, employee, checkin=False):
        # Fetch the cursor to execute the queries
        cr = self._cr
        user = self.env.user
        checkin_diff = check_in_status = checkout_diff = checkout_status = False
        if checkin:
            # Fetch the Starting Hour for a particular day to Match against the
            # CheckIn
            check_in_dt = datetime.strptime(checkin, DEFAULT_SERVER_DATETIME_FORMAT)
            local_tz = pytz.timezone(user.tz or 'UTC')
            ci_dt = check_in_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
            qry = '''select hour_from
                    from resource_calendar rc, \
                    resource_calendar_attendance rca
                    where rc.id = rca.calendar_id and
                    rc.id = %s and \
                    dayofweek=%s'''
            qry1 = qry + " and %s between date_from and date_to order by \
                hour_from limit 1"
            if not employee.calendar_id:
                raise ValidationError(_('Please Configure Working Time in Employee!'))
            params1 = (employee.calendar_id.id, str(ci_dt.weekday()), checkin)
            cr.execute(qry1, params1)
            res = cr.fetchone()
            # If specific dates are not given then fetch the records that do
            # not have dates
            if not res:
                qry2 = qry + " order by hour_from limit 1"
                params2 = (employee.calendar_id.id, str(ci_dt.weekday()))
                cr.execute(qry2, params2)
                res = cr.fetchone()
            hour_from = res and res[0] or 0.0

            #############################################
            # newdate = check_in_dt.replace(hour=8, minute=0)
            # newdate2 = newdate.replace(tzinfo=pytz.utc).astimezone(local_tz)
            # newdate2_diff = newdate2.hour + (newdate2.minute * 100 / 60) / 100.0
            #############################################
            # local = pytz.timezone("America/Los_Angeles")
            # naive = datetime.datetime.strptime("2001-2-3 08:00:00", "%Y-%m-%d %H:%M:%S")
            # local_dt = local.localize(naive, is_dst=None)
            # utc_dt = local_dt.astimezone(pytz.utc)
            #############################################

            # Converting the Hours and Minutes to Float to match as
            # odoo Standard.
            checkin_time = ci_dt.hour + (ci_dt.minute * 100 / 60) / 100.0

            # Get the Check In Difference
            checkin_diff = checkin_time - hour_from
            # Generate the CheckIn Status as per the CheckIn time
            check_in_status = 'ontime'
            if checkin_diff > 0:
                check_in_status = 'late'
            elif checkin_diff < 0:
                check_in_status = 'early'
        return checkin_diff, check_in_status


class hr_timesheet_sheet_sheet_day_inherit(models.Model):
    _inherit = "hr_timesheet_sheet.sheet.day"

    @api.multi
    def _compute_hours(self):
        for rec in self:
            period = {
                'date_from': rec.name,
                'date_to': rec.name
            }
            dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(rec.name), until=parser.parse(rec.name)))
            for date_line in dates:
                dh = rec.sheet_id.calculate_duty_hours_ex(date_from=date_line,period=period)
                rec.contracthours = dh
                # rec.overtimehours = rec.total_attendance - dh
                under_overtime = rec.total_attendance - dh

                late_time = 0.00
                attandance = self.env['hr.attendance'].sudo().search([
                    ('employee_id', '=', rec.sheet_id.employee_id.id),
                    ('date_dt', '=', rec.name)
                ], limit=1, order='id asc')
                if attandance:
                    attandance_diff = attandance.get_diff1(rec.sheet_id.employee_id, attandance.check_in)
                    late_time = attandance_diff[0]
                    # late_time = attandance.checkin_diff

                late = 0.00
                early = 0.00
                if late_time < 0:
                    late = float(late_time) * (-1)
                elif late_time > 0:
                    early = float(late_time) * (1)

                rec.late = late
                rec.early = early

                if under_overtime < 0:
                    rec.overtimehours = 0.00
                    rec.undertime = under_overtime
                else:
                    rec.overtimehours = under_overtime - late
                    rec.undertime = 0.00

                # code for ot 1, 1.5 and 2 hours
                ot1_hours = 0.00
                ot1_5_hours = 0.00
                ot2_hours = 0.00
                day_line = date_line.strftime("%A")
                # last_record = self.env['hr.employee.config.settings'].sudo().search([], limit=1, order='id desc')
                last_record = self.env.user.company_id
                public_holidays = self.env['hr.holiday.lines'].search(
                    [('holiday_date', '=', rec.name),('state', 'in', ('confirmed','validated'))])
                if (public_holidays and last_record.ot1_monday and public_holidays.day in ['Monday']) or\
                    (public_holidays and last_record.ot1_tuesday and public_holidays.day in ['Tuesday']) or\
                    (public_holidays and last_record.ot1_wednesday and public_holidays.day in ['Wednesday']) or\
                    (public_holidays and last_record.ot1_thursday and public_holidays.day in ['Thursday']) or \
                    (public_holidays and last_record.ot1_friday and public_holidays.day in ['Friday']) or \
                    (public_holidays and last_record.ot1_saturday and public_holidays.day in ['Saturday']) or \
                    (public_holidays and last_record.ot1_sunday and public_holidays.day in ['Sunday']):
                    if (rec.overtimehours) > 0:
                        ot1_hours = rec.overtimehours
                    # if (rec.total_attendance - rec.contracthours) > 0:
                    #     ot1_hours = rec.total_attendance - rec.contracthours
                elif (last_record.ot1_5_monday and day_line in ['Monday']) or\
                    (last_record.ot1_5_tuesday and day_line in ['Tuesday']) or\
                    (last_record.ot1_5_wednesday and day_line in ['Wednesday']) or\
                    (last_record.ot1_5_thursday and day_line in ['Thursday']) or \
                    (last_record.ot1_5_friday and day_line in ['Friday']) or \
                    (last_record.ot1_5_saturday and day_line in ['Saturday']) or \
                    (last_record.ot1_5_sunday and day_line in ['Sunday']):
                    if (rec.overtimehours) > 0:
                        ot1_5_hours = rec.overtimehours
                    # if (rec.total_attendance - rec.contracthours) > 0:
                    #     ot1_5_hours = rec.total_attendance - rec.contracthours
                elif (public_holidays and last_record.ot2_saturday and public_holidays.day in ['Saturday']) or\
                    (public_holidays and last_record.ot2_sunday and public_holidays.day in ['Sunday']):
                    # or\
                    # (last_record.ot2_saturday and day_line in ['Saturday']) or \
                    # (last_record.ot2_sunday and day_line in ['Sunday']):
                    if (rec.overtimehours) > 0:
                        ot2_hours = rec.overtimehours
                    # if (rec.total_attendance - rec.contracthours) > 0:
                    #     ot2_hours = rec.total_attendance - rec.contracthours

                rec.ot1_hours = ot1_hours
                rec.ot1_5_hours = ot1_5_hours
                rec.ot2_hours = ot2_hours

    contracthours = fields.Float('Contract Hours', compute='_compute_hours')
    overtimehours = fields.Float('Total Overtime', compute='_compute_hours')
    late = fields.Float('Late', compute='_compute_hours')
    early = fields.Float('Early', compute='_compute_hours')
    undertime = fields.Float('Undertime', compute='_compute_hours')
    ot1_hours = fields.Float('OT 1.0 Hours', compute='_compute_hours', help="Employee works on public holidays.")
    ot1_5_hours = fields.Float('OT 1.5 Hours', compute='_compute_hours', help="Employee works overtime on normal working days.")
    ot2_hours = fields.Float('OT 2.0 Hours', compute='_compute_hours', help="Total overtime hours on weekend.")
