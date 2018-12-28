# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services Pvt. Ltd.
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

#openerp.tools.safe_eval._ALLOWED_MODULES.append('math')


class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    branch_id = fields.Char("Branch ID", size=48)

class payroll_extended(models.Model):
    _inherit = 'hr.payslip.input'

    code = fields.Char('Code', size=52, required=False, readonly=False, help="The code that can be used in the salary rules")
    contract_id = fields.Many2one('hr.contract', 'Contract', required=False, help="The contract for which applied this input")

class hr_payslip_worked_days(models.Model):
    _inherit = 'hr.payslip.worked_days'

    code = fields.Char('Code', size=52, required=False, readonly=False, help="The code that can be used in the salary rules")
    contract_id = fields.Many2one('hr.contract', 'Contract', required=False, help="The contract for which applied this input")

class hr_payslip_line(models.Model):
    _inherit = 'hr.payslip.line'

    contract_id = fields.Many2one('hr.contract', 'Contract', required=False, index=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=False)

class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'

    code = fields.Char('Code', size=64, required=False, help="The code of salary rules can be used as reference in computation of other rules. In that case, it is case sensitive.")
    id = fields.Integer('ID', readonly=True)
    race_id = fields.Many2one('employee.race', string="Employee Race")

    @api.multi
    def compute_rule(self, localdict):
        if localdict is None or not localdict:
            localdict = {}
        localdict.update({'math': math})
        return super(hr_salary_rule, self).compute_rule(localdict)


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
            if payslip.employee_id.user_id:
                account_analytic_search_ids = self.env['account.analytic.line'].search([('user_id', '=', payslip.employee_id.user_id.id), 
                                                                                        ('date', '>=', payslip.date_from),
                                                                                        ('date', '<=', payslip.date_to),
                                                                                        ('date', 'in', pub_holi_days)])
                if account_analytic_search_ids and account_analytic_search_ids.ids:
                    for timesheet in account_analytic_search_ids:
                        total_hours = total_hours + timesheet.unit_amount or 0.0
                        self.pub_holiday_hours = total_hours

    @api.multi
    @api.depends('employee_id.user_id', 'date_from', 'date_to','employee_id')
    def _get_total_hours(self):
        for payslip in self:
            total_timesheet_hours = 0.0
            if payslip.employee_id.user_id:
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
            total_overtime = 0.0
            if total_timesheet_hours > self.total_hours:
                total_overtime = total_timesheet_hours - self.total_hours
                self.overtime_hours = total_overtime


    cheque_number = fields.Char("Cheque Number", size=64)
    active = fields.Boolean('Pay', default=True)
    pay_by_cheque = fields.Boolean('Pay By Cheque')
    employee_name = fields.Char(related='employee_id.name', string="Employee Name", store=True)
    active_employee = fields.Boolean(related='employee_id.active', string="Active Employee")
    total_timesheet_hours = fields.Float(compute = '_get_total_hours', string='Total Timesheet Hours')
    total_hours = fields.Float(compute = '_get_total_hours', string='Total Hours')
    overtime_hours = fields.Float(compute = '_get_total_hours', string='Overtime Hours')
    pub_holiday_hours = fields.Float(compute = '_get_total_public_holiday_hours', string='Public Holiday Hours')
    date = fields.Date(string="Payment Date")

#    @api.onchange('employee_id', 'date_from','date_to','contract_id')
#    def onchange_employee(self):
#        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
#            return
#        employee_id = self.employee_id.id
#        date_from = self.date_from
#        date_to = self.date_to
#        contract_id = self.contract_id and self.contract_id.id or False

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day):
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

        res = []
        for contract in self.env['hr.contract'].browse(contract_ids):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            leaves = {}
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
#                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                working_hours_on_day = contract.working_hours.working_hours_on_day(day_from + timedelta(days=day))
                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day))
                    if leave_type and leave_type['name']:
                        #if he was on leave, fill the leaves dict
                        if leave_type['name'] in leaves:
                            leaves[leave_type['name']]['number_of_days'] +=  leave_type['days']
                            if leave_type['half_work'] == True:
                                leaves[leave_type['name']]['number_of_hours'] += working_hours_on_day/2
                            else:
                                leaves[leave_type['name']]['number_of_hours'] += working_hours_on_day
                        else:
                            if leave_type['half_work'] == True:
                                working_hours_on_day = working_hours_on_day/2
                            leaves[leave_type['name']] = {
                                'name': leave_type['name'],
                                'sequence': 5,
                                'code': leave_type['name'],
                                'number_of_days': leave_type['days'],
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves
        return res


    @api.onchange('employee_id', 'date_from','date_to','contract_id')
    def onchange_employee(self):
        if self.employee_id and self.employee_id.id:
            employee_id = self.employee_id and self.employee_id.id
        else:
            employee_id =  self._context.get('employee_id', False)

        if self.date_from:
            date_from = self.date_from
        else:
            date_from =  self._context.get('date_from', False)

        if self.date_to:
            date_to = self.date_to
        else:
            date_to =  self._context.get('date_to', False)

        if self.contract_id and self.contract_id.id:
            contract_id = self.contract_id and self.contract_id.id
        else:
            contract_id =  self._context.get('contract_id', False)

        if (not employee_id) or (not date_from) or (not date_to):
            return {}

        empolyee_obj = self.env['hr.employee']
        period_start_date = date_from
        period_end_date = date_to
        s_contract_id =[]
            #delete old worked days lines
        old_worked_days_ids = []
        if self.id:
            old_worked_days_ids = [worked_days_rec.id for  worked_days_rec in self.env['hr.payslip.worked_days'].search([('payslip_id', '=', self.id)])]
        if old_worked_days_ids:
            self._cr.execute(""" delete from hr_payslip_worked_days where id in %s""",(tuple(old_worked_days_ids),))
        #delete old input lines
        old_input_ids = []
        if self.id :
            old_input_ids = [input_rec.id for input_rec in self.env['hr.payslip.input'].search([('payslip_id', '=', self.id)])]
        if old_input_ids:
            self._cr.execute(""" delete from hr_payslip_input where id in %s""",(tuple(old_input_ids),))
        res = {'value':{
                      'line_ids':[],
                      'input_line_ids': [],
                      'worked_days_line_ids': [],
                      #'details_by_salary_head':[], TODO put me back
                      'name':'',
                      'contract_id': False,
                      'struct_id': False,
                      }
            }
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        employee_brw = empolyee_obj.browse(employee_id)
        res['value'].update({
                    'name': _('Salary Slip of %s for %s') % (employee_brw.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                    'company_id': employee_brw.company_id and employee_brw.company_id.id or False
        })
        if not self._context.get('contract', False):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(employee_brw, date_from, date_to)
            s_contract_id =contract_ids 
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
                s_contract_id =contract_ids
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(employee_brw, date_from, date_to)
                s_contract_id =contract_ids
        if not contract_ids:
            return res
        contract_record = self.env['hr.contract'].browse(contract_ids[0])
        res['value'].update({'contract_id': contract_record and contract_record.id or False})
        struct_record = contract_record and contract_record.struct_id or False
        if not struct_record:
            return res
        res['value'].update({
                    'struct_id': struct_record.id,
        })
        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(contract_ids, date_from, date_to)
        input_line_ids = self.get_inputs(contract_ids, date_from, date_to)
        res['value'].update({
                    'worked_days_line_ids': worked_days_line_ids,
                    'input_line_ids': input_line_ids,
        })
        if not employee_id:
            return res
        active_employee = empolyee_obj.browse(employee_id).active
        res['value'].update({'active_employee': active_employee})
        res['value'].update({'employee_id': employee_id, 'date_from': date_from, 'date_to': date_to})
        if date_from and date_to:
            current_date_from = date_from
            current_date_to = date_to
            date_from_cur = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
            previous_month_obj = parser.parse(date_from_cur.strftime(DEFAULT_SERVER_DATE_FORMAT)) - relativedelta(months=1)
            total_days = calendar.monthrange(previous_month_obj.year, previous_month_obj.month)[1]
            first_day_of_previous_month = datetime.strptime("1-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
            last_day_of_previous_month = datetime.strptime(str(total_days) + "-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
            date_from = datetime.strftime(first_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
            date_to = datetime.strftime(last_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
            dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(date_from), until=parser.parse(date_to)))
            sunday = saturday = weekdays = 0
            for day in dates:
                if day.weekday() == 5:
                    saturday += 1
                elif day.weekday() == 6:
                    sunday += 1
                else:
                    weekdays += 1
            new = {'code':'TTLPREVDAYINMTH','name':'Total number of days for previous month','number_of_days':len(dates), 'sequence': 2, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLPREVSUNINMONTH','name':'Total sundays in previous month','number_of_days':sunday, 'sequence': 3, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLPREVSATINMONTH','name':'Total saturdays in previous month','number_of_days':saturday, 'sequence': 4, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLPREVWKDAYINMTH','name':'Total weekdays in previous month','number_of_days':weekdays, 'sequence': 5, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)

#             =============added no holidays in current month==========
            f = period_end_date
            count = 0
            currentz_yearz = datetime.strptime(f, DEFAULT_SERVER_DATE_FORMAT).year
            currentz_mnthz = datetime.strptime(f, DEFAULT_SERVER_DATE_FORMAT).month

#            holiday_data = self.env['hr.holiday.public'].search([])
#            for line in holiday_data:
#                holiday_lines = line.holiday_line_ids
#                if line.state =='validated':
#                    for holiday in holiday_lines:
#                        holiday_date = holiday.holiday_date
#                        holidyz_mnth = datetime.strptime(holiday_date, DEFAULT_SERVER_DATE_FORMAT).month
#                        holiday_year = datetime.strptime(holiday_date, DEFAULT_SERVER_DATE_FORMAT).year
#                        if currentz_yearz == holiday_year:
#                            if holidyz_mnth == currentz_mnthz:
#                                count = count+1
#                 appending values into workday_lines in hr payroll

            holiday_brw = self.env['hr.holiday.public'].search([('state','=','validated')])
            if holiday_brw and holiday_brw.ids:
                for line in holiday_brw:
                    if line.holiday_line_ids and line.holiday_line_ids.ids:
                        for holiday in line.holiday_line_ids:
                            holidyz_mnth = datetime.strptime(holiday.holiday_date, DEFAULT_SERVER_DATE_FORMAT).month
                            holiday_year = datetime.strptime(holiday.holiday_date, DEFAULT_SERVER_DATE_FORMAT).year
                            if currentz_yearz == holiday_year and holidyz_mnth == currentz_mnthz:
                                count = count+1

            new = {'code':'PUBLICHOLIDAYS','name':'Total Public Holidays in current month','number_of_days':count, 'sequence': 6, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)

#             ===============end of holiday calculation===========
            this_month_obj = parser.parse(date_from_cur.strftime(DEFAULT_SERVER_DATE_FORMAT)) + relativedelta(months=1,days= -1)
            dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(current_date_from), until=parser.parse(current_date_to)))
            total_days_cur_month = calendar.monthrange(this_month_obj.year, this_month_obj.month)[1]
            first_day_of_current_month = datetime.strptime("1-" + str(this_month_obj.month) + "-" + str(this_month_obj.year) , '%d-%m-%Y')
            last_day_of_current_month = datetime.strptime(str(total_days_cur_month) + "-" + str(this_month_obj.month) + "-" + str(this_month_obj.year) , '%d-%m-%Y')
            th_current_date_from = datetime.strftime(first_day_of_current_month, DEFAULT_SERVER_DATE_FORMAT)
            th_current_date_to = datetime.strftime(last_day_of_current_month, DEFAULT_SERVER_DATE_FORMAT)
            cur_dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(th_current_date_from), until=parser.parse(th_current_date_to)))
            sunday = saturday = weekdays = 0
            cur_sunday = cur_saturday = cur_weekdays = 0
            for day in dates:
                if day.weekday() == 5:
                    saturday += 1
                elif day.weekday() == 6:
                    sunday += 1
                else:
                    weekdays += 1
            for day in cur_dates:
                if day.weekday() == 5:
                    cur_saturday += 1
                elif day.weekday() == 6:
                    cur_sunday += 1
                else:
                    cur_weekdays += 1
            new = {'code':'TTLDAYINMTH','name':'Total days for current month','number_of_days':len(cur_dates), 'sequence': 7, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLCURRDAYINMTH','name':'Total number of days for current month','number_of_days':len(dates), 'sequence': 2, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLCURRSUNINMONTH','name':'Total sundays in current month','number_of_days':sunday, 'sequence': 3, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLCURRSATINMONTH','name':'Total saturdays in current month','number_of_days':saturday, 'sequence': 4, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLCURRWKDAYINMTH','name':'Total weekdays in current month','number_of_days':weekdays, 'sequence': 5, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLCURRWKDAYINHMTH','name':'Total weekdays in whole current month','number_of_days':cur_weekdays, 'sequence': 8, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            cur_month_weekdays = 0

#            if contract_record:
#                contract_start_date = contract_record.date_start
#                contract_end_date = contract_record.date_end
#                if contract_start_date:
#                    if contract_start_date <= current_date_from and contract_end_date >= current_date_to:
##                    if contract_start_date >= current_date_from and contract_start_date >= current_date_to:
#                        current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(current_date_from), until=parser.parse(current_date_to)))
#                        for day in current_month_days:
#                            if day.weekday() not in [5,6]:
#                                cur_month_weekdays += 1
#                    else:
#                        if contract_start_date <= current_date_from and contract_end_date <= current_date_to:
#                            current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(current_date_from), until=parser.parse(contract_end_date)))
#                            for day in current_month_days:
#                                if day.weekday() not in [5,6]:
#                                    cur_month_weekdays += 1
#                elif contract_end_date:
#
#                    if contract_end_date >= current_date_from and contract_end_date <= current_date_to:
#                        current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(current_date_from), until=parser.parse(contract_end_date)))
#                        for day in current_month_days:
#                            if day.weekday() not in [5,6]:
#                                cur_month_weekdays += 1
            if contract_record:
                contract_start_date = contract_record.date_start
                contract_end_date = contract_record.date_end
                if contract_start_date and contract_end_date:

                    if current_date_from <= contract_start_date and contract_end_date <= current_date_to:
                        current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(contract_start_date), until=parser.parse(contract_end_date)))
                        for day in current_month_days:
                            if day.weekday() not in [5,6]:
                                cur_month_weekdays += 1

                    elif current_date_from <= contract_start_date and current_date_to <= contract_end_date :
                        current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(contract_start_date), until=parser.parse(current_date_to)))
                        for day in current_month_days:
                            if day.weekday() not in [5,6]:
                                cur_month_weekdays += 1

                    elif contract_start_date <= current_date_from and contract_end_date <= current_date_to:
                        current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(current_date_from), until=parser.parse(contract_end_date)))
                        for day in current_month_days:
                            if day.weekday() not in [5,6]:
                                cur_month_weekdays += 1

            if cur_month_weekdays:
                new = {'code':'TTLCURCONTDAY','name':'Total current contract days in current month','number_of_days':cur_month_weekdays, 'sequence': 6, 'contract_id': contract_record.id}
                res.get('value').get('worked_days_line_ids').append(new)
            else:
                new = {'code':'TTLCURCONTDAY','name':'Total current contract days in current month','number_of_days':weekdays, 'sequence': 6, 'contract_id': contract_record.id}
                res.get('value').get('worked_days_line_ids').append(new)
        if employee_id:
            emp_obj = self.env["hr.employee"]
            emp_rec = emp_obj.browse(employee_id)
            holiday_status_obj = self.env["hr.holidays.status"]
            if emp_rec.leave_config_id:
                for h_staus in emp_rec.leave_config_id.holiday_group_config_line_ids:
                    flag = False
                    for payslip_data in res["value"].get("worked_days_line_ids"):
                        if payslip_data.get("code") == h_staus.leave_type_id.name:
                            flag = True
                    if not flag:
                        new = {'code':h_staus.leave_type_id.name, 'name':h_staus.leave_type_id.name2, 'number_of_days':0.0, 'sequence': 0, 'contract_id': contract_record.id}
                        res.get('value').get('worked_days_line_ids').append(new)
            else:
                holidays_status_ids = holiday_status_obj.search([])
                for holiday_status in holidays_status_ids:
                    flag = False
                    for payslip_data in res["value"].get("worked_days_line_ids"):
                        if payslip_data.get("code") == holiday_status.name:
                            flag = True
                    if not flag:
                        new = {'code':holiday_status.name, 'name':holiday_status.name2, 'number_of_days':0.0, 'sequence': 0, 'contract_id': contract_record.id}
                        res.get('value').get('worked_days_line_ids').append(new)
        return res

    @api.multi
    def compute_sheet(self):
        result = super(hr_payslip, self).compute_sheet()
        # emp_race_obj = self.env['employee.race'].sudo()
        # hr_salary_rule_obj = self.env['hr.salary.rule'].sudo()
        hr_payslip_line_obj = self.env['hr.payslip.line'].sudo()
        for payslip in self:
            net_salary = hr_payslip_line_obj.search(
                [('slip_id', '=', payslip.id), ('category_id.code', '=', 'NET')])
            employee = payslip.contract_id and payslip.contract_id.employee_id or False
            if employee and (employee.singaporean or employee.pr_year) and employee.employee_race_id:
                for line in payslip.line_ids:
                    if line.salary_rule_id and line.salary_rule_id.race_id \
                        and (line.salary_rule_id.race_id.id != employee.employee_race_id.id):
                        net_salary.amount = net_salary.amount + line.amount
                        line.sudo().unlink()
            else:
                for one_line in hr_payslip_line_obj.search(
                        [('slip_id', '=', payslip.id), ('salary_rule_id.race_id', '!=', False)]):
                    net_salary.amount = net_salary.amount + one_line.amount
                    one_line.sudo().unlink()

            # employee = payslip.contract_id and payslip.contract_id.employee_id or False
            # muslim_race = emp_race_obj.search([('name', '=', 'Muslims')], limit=1)
            # chinese_race = emp_race_obj.search([('name', '=', 'Chinese')], limit=1)
            # indian_race = emp_race_obj.search([('name', '=', 'Indian')], limit=1)
            # eurasian_race = emp_race_obj.search([('name', '=', 'Eurasian')], limit=1)
            #
            # muslim_salary_rule = hr_salary_rule_obj.search([('code', '=', 'CPFMBMF')], limit=1)
            # chinese_salary_rule = hr_salary_rule_obj.search([('code', '=', 'CPFCDAC')], limit=1)
            # indian_salary_rule = hr_salary_rule_obj.search([('code', '=', 'CPFSINDA')], limit=1)
            # eurasian_salary_rule = hr_salary_rule_obj.search([('code', '=', 'CPFECF')], limit=1)
            #
            # other_salary_rules_ids = []
            # if employee and (employee.singaporean or employee.pr_year) and employee.employee_race_id:
            #     if muslim_race and employee and employee.employee_race_id.id and employee.employee_race_id.id == muslim_race.id:
            #         other_salary_rules_ids = [chinese_salary_rule.id, indian_salary_rule.id, eurasian_salary_rule.id]
            #
            #     elif chinese_race and employee and employee.employee_race_id.id and employee.employee_race_id.id == chinese_race.id:
            #         other_salary_rules_ids = [indian_salary_rule.id, eurasian_salary_rule.id, muslim_salary_rule.id]
            #
            #     elif indian_race and employee and employee.employee_race_id.id and employee.employee_race_id.id == indian_race.id:
            #         other_salary_rules_ids = [chinese_salary_rule.id, eurasian_salary_rule.id, muslim_salary_rule.id]
            #
            #     elif eurasian_race and employee and employee.employee_race_id.id and employee.employee_race_id.id == eurasian_race.id:
            #         other_salary_rules_ids = [chinese_salary_rule.id, indian_salary_rule.id, muslim_salary_rule.id]
            #
            #     else:
            #         other_salary_rules_ids = [chinese_salary_rule.id, indian_salary_rule.id, eurasian_salary_rule.id, muslim_salary_rule.id]
            # else:
            #     other_salary_rules_ids = [chinese_salary_rule.id, indian_salary_rule.id, eurasian_salary_rule.id, muslim_salary_rule.id]
            #
            # if other_salary_rules_ids:
            #     payslip_lines = hr_payslip_line_obj.search(
            #         [('slip_id', '=', payslip.id), ('salary_rule_id', 'in', other_salary_rules_ids)])
            #     for one_line in payslip_lines:
            #         one_line.sudo().unlink()
            #         # one_line.sudo().write({
            #         #     'quantity': 0,
            #         #     'amount': 0,
            #         #     'rate': 0,
            #         # })

        return result

            # @api.multi
    # def compute_sheet(self):
    #     result = super(hr_payslip, self).compute_sheet()
    #     print"result:", result
    #     lines = []
    #     for payslip in self:
    #         print"payslip:", payslip
    #         for line in payslip.line_ids:
    #             print"lineeee:", line
    #             if line.amount == 0:
    #                 lines.append(line.id)
    #                 print"lines:", lines
    #     if lines:
    #         line_rec = self.env['hr.payslip.line'].browse(lines)
    #         print"linerec:", line_rec
    #         line_rec.unlink()
    #     return result


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    identification_no = fields.Selection(selection=[('1', 'NRIC'),('2', 'FIN'), 
                                                    ('3', 'Immigration File Ref No.'),('4', 'Work Permit No'),
                                                    ('5', 'Malaysian I/C (for non-resident director and seaman only)'),
                                                    ('6', 'Passport No. (for non-resident director and seaman only)')],
                                         string='2. ID Type of Employee')
    address_type = fields.Selection(selection=[('L', 'Local residential address'),('F', 'Foreign address'),
                                               ('C', 'Local C/O address'),
                                               ('N', 'Not Available')], string='Address Type')
    empcountry_id = fields.Many2one('employee.country', '6(k). Country Code of address')
    empnationality_id = fields.Many2one('employee.nationality', '7. Nationality Code')
    cessation_provisions = fields.Selection(selection=[('Y', 'Cessation Provisions applicable'),
                                                       ('N', 'Cessation Provisions not applicable')], string='28. Cessation Provisions')
    employee_type = fields.Selection(selection=[('full_employeement', 'Full Employer & Graduated Employee (F/G)'),
                                              ('graduated_employee', 'Graduated Employer & Employee (G/G)')], string='Employee Type', default='full_employeement')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self.env.context
        """
            Override Search method for put filter on current working status. 
        """
        if context and context.get('batch_start_date') and context.get('batch_end_date'):
            active_contract_employee_list = []
            contract_ids = self.env['hr.contract'].search(['|', ('date_end', '>=', context.get('batch_start_date')), 
                                                           ('date_end', '=', False),
                                                           ('date_start', '<=', context.get('batch_end_date'))])
            for contract in contract_ids:
                active_contract_employee_list.append(contract.employee_id.id)
            args.append(('id', 'in', active_contract_employee_list))
        return super(hr_employee, self).search(args, offset, limit, order, count=count)


class employee_country(models.Model):
    _name = 'employee.country'

    name = fields.Char('Country', size=32, required=True)
    code = fields.Integer('Code', size=3, required=True)

class employee_nationality(models.Model):
    _name = 'employee.nationality'

    name = fields.Char('Nationality', size=32, required=True)
    code = fields.Integer('Code', size=3, required=True)

class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'

    @api.multi
    def open_payslip_employee(self):
        cr,uid,context = self.env.args
        if context is None:
            context = {}
        context = dict(context)
        context.update({'default_date_start': self.date_start, 'default_date_end': self.date_end})
        return {'name': ('Payslips by Employees'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.payslip.employees',
                'type': 'ir.actions.act_window',
                'target': 'new',
        }

class hr_payslip_employees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    date_start = fields.Date('Date From')
    date_end = fields.Date('Date To')



    @api.multi
    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].with_context(date_from=from_date, date_to=to_date, employee_id=employee.id, contract_id=False).onchange_employee()
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
            }
            payslips += self.env['hr.payslip'].create(res)
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}


class res_users(models.Model):
    _inherit = 'res.users'

    user_ids = fields.Many2many('res.users', 'ppd_res_user_payroll_rel','usr_id','user_id','User Name')

class res_company(models.Model):
    _inherit = 'res.company'

    company_code = fields.Char('Company Code')

class res_partner(models.Model):
    _inherit = 'res.partner'

    level_no = fields.Char('Level No')
    house_no = fields.Char('House No')
    unit_no = fields.Char('Unit No')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: