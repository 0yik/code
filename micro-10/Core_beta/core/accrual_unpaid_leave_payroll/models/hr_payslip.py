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

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day):
            res1 = {'name':False, 'days':0.0, 'half_work':False}
            day = datetime_day.strftime("%Y-%m-%d")
#             holiday_ids = self.env['hr.holidays'].search([('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            holiday_ids = self.env['hr.holidays'].search([('state', '=', 'validate'),
                                                          ('employee_id', '=', employee_id),
                                                          ('payslip_status', '=', False),
                                                          ('type', '=', 'remove'),
                                                          ('date_from','<=', day),
                                                          ('date_to', '>=', day)])
            if holiday_ids:
                holiday.append(holiday_ids[0].id)
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
            holiday = []
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
            total_days = 0
            for leave in leaves:
                if leave['code']=='UP':
                    day_from = day_from + relativedelta(months=-1)
                    holiday_browse_ids = self.env['hr.holidays'].search([('state', '=', 'validate'),
                                                                  ('employee_id', '=', contract.employee_id.id),
                                                                  ('payslip_status', '=', False),
                                                                  ('type', '=', 'remove'),
                                                                  ('holiday_status_id.name','=', 'UP'),
                                                                  ('date_from', '>=', str(day_from)),
                                                                  ('date_from', '<=', str(day_to))])
                    leave['number_of_days'] = sum([record.number_of_days_temp for record in holiday_browse_ids]) + leave['number_of_days']
            res += [attendances] + leaves
            if self._context.get('return_dict',False):
                return holiday
        return res

    @api.multi
    def action_payslip_done(self):
        res = super(hr_payslip, self).action_payslip_done()
        for rec in self:
            contract_ids = self.get_contract(rec.employee_id, rec.date_from, rec.date_to)
            lines = self.with_context({'return_dict':True}).get_worked_day_lines(contract_ids, rec.date_from, rec.date_to)
            if lines:
                holidays = self.env['hr.holidays'].browse(lines)
                holidays.update({'payslip_status' : True})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: