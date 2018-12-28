from odoo import api, fields, models, tools, _

import time
from dateutil import parser, rrule
import math
import calendar
import odoo.tools as tools
from datetime import date, datetime, timedelta
from odoo import fields, api, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta

import babel

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    termination_payslip = fields.Boolean('Termination Payslip')

    @api.multi
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for rec in self:
            if rec.termination_payslip:
                install_lines = self.env['loan.installment.details'].search([('employee_id','=',rec.employee_id.id), ('state', '!=','paid'), ('loan_repayment_method','=','salary')])
                install_lines.pay_installment()
            else:
                line = rec.line_ids.filtered(lambda l:l.salary_rule_id.is_loan_payment)
                if line:
                    install_ids = self.get_loan_installment(rec.employee_id.id, rec.date_from, rec.date_to)
                    if install_ids:
                        install_lines = self.env['loan.installment.details'].browse(install_ids)
                        install_lines.pay_installment()
        return res

    @api.onchange('employee_id', 'date_from','date_to','contract_id')
    def onchange_employee(self):
        empolyee_obj = self.env['hr.employee']
        if self.employee_id and self.employee_id.id:
            employee_id = self.employee_id and self.employee_id.id
        else:
            employee_id =  self._context.get('employee_id', False)
        employee_brw = empolyee_obj.browse(employee_id)
        if self.date_from:
            date_from = self.date_from
        else:
            date_from =  self._context.get('date_from', False)

        if self.date_to:
            date_to = self.date_to
        else:
            date_to =  self._context.get('date_to', False)
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
        if self:
            if employee_brw.cessation_date >= date_from and employee_brw.cessation_date <= date_to:
                self.date_to = employee_brw.cessation_date
                date_to = employee_brw.cessation_date
                self.termination_payslip = True
            else:
                self.termination_payslip = False
        else:
            if employee_brw.cessation_date >= date_from and employee_brw.cessation_date <= date_to:
                res['value']['date_to'] = employee_brw.cessation_date
                date_to = employee_brw.cessation_date
                res['value']['termination_payslip'] = True
            else:
                res['value']['termination_payslip'] = False

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
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))

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
