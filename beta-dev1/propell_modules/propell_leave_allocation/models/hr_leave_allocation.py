from odoo import api, fields, models, _
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
# import logging
# _logger = logging.getLogger(__name__)

class allocate_leave_reason(models.Model):

    _name = 'allocate.leaves.reason'

    allocate_leave_id = fields.Many2one('allocate.leaves')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    reason = fields.Char(string="Reason")

class allocate_leave(models.TransientModel):

    _inherit = 'allocate.leaves'

    leave_reason_ids = fields.One2many('allocate.leaves.reason', 'allocate_leave_id')

    @api.multi
    def allocate_leaves(self):
        res_id = self.env['allocate.leaves'].create({})
        reason_vals = []
        emp_ids = []
        if self.holiday_status_id.name == 'AL':
            for emp in self.employee_ids:
                joining_date = datetime.datetime.strptime(emp.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
                today_date = datetime.datetime.today().date()
                holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id), 
                                                              ('type', '=', 'add'), 
                                                              ('holiday_status_id', '=', self.holiday_status_id.id),
                                                              ('hr_year_id', '=', self.fiscal_year_id.id)
                                                              ])
                leave_days = 0
                for holiday in holiday_ids:
                    leave_days += holiday.number_of_days_temp
                if (today_date - joining_date).days < (365 * 2) and int(self.no_of_days + leave_days) != 7:
                    if leave_days > 0.0:
                        reason = ('The leave is already allocated to (Employee Name). If you wish to change the allocation, please refuse the allocated leave, Reset it to Draft and proceed with the changes.')
                    else:
                        reason = ('Leave allocation should be 7 days for the employees less than 2 years of service or for worker/technician.')
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
#                     raise ValidationError(_('Warning \n You can allocate 7 days for one year experiance Employee for %s Employee') % (emp.name))
                if (today_date - joining_date).days > (365 * 2) and (today_date - joining_date).days <= (365 * 8) and int(self.no_of_days + leave_days) != 14:
                    if leave_days > 0.0:
                        reason = ('The leave is already allocated to (Employee Name). If you wish to change the allocation, please refuse the allocated leave, Reset it to Draft and proceed with the changes.')
                    else:
                        reason = ('Leave allocation should be 14 days for the employees equal or greater than 2 years of service.')
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
#                     raise ValidationError(_('Warning \n You can allocate 14 days for two year experiance Employee for %s Employee') % (emp.name))
                if (today_date - joining_date).days > (365 * 8) and int(self.no_of_days + leave_days) != 21:
                    if leave_days > 0.0:
                        reason = ('The leave is already allocated to (Employee Name). If you wish to change the allocation, please refuse the allocated leave, Reset it to Draft and proceed with the changes.')
                    else:
                        reason = ('Leave allocation should be 21 days for the employees equal or greater than 8 years of service.')
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
#                     raise ValidationError(_('Warning \n You can allocate 21 days for eight year experiance Employee for %s Employee') % (emp.name))

        if self.holiday_status_id.name == 'CCL':
            for emp in self.employee_ids:

                joining_date = datetime.datetime.strptime(emp.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
                today_date = datetime.datetime.today().date()
                if (today_date - joining_date).days < 90:
                    reason = ('Employee %s should have 3+ months experiance in same company.') % (emp.name)
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)

                holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id),
                                                              ('type', '=', 'add'),
                                                              ('holiday_status_id', '=', self.holiday_status_id.id),
                                                              ('hr_year_id', '=', self.fiscal_year_id.id),
                                                              ])
                leave_days = 0
                for holiday in holiday_ids:
                    leave_days += holiday.number_of_days_temp

                temp = emp.dependent_ids and emp.dependent_ids[0].birth_date
                if temp:
                    temp = datetime.datetime.strptime(temp, DEFAULT_SERVER_DATE_FORMAT).date()
                for dependent in emp.dependent_ids:
                    birth = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
                    if birth > temp:
                        temp = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
                if temp:
                    to_date = datetime.datetime.strptime(fields.Date.today() + " 00:00:00", DEFAULT_SERVER_DATETIME_FORMAT).date()
                    temp = temp + relativedelta(years=7)

                    if emp.singaporean:
                        if to_date > temp:
                            reason = ('Child should below 7 year old, of %s Employee') % (emp.name)
                            reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                            emp_ids.append(emp.id)
#                             raise ValidationError(_('Warning \n Child should below 7 year old, of %s Employee') % (emp.name))
                        if int(self.no_of_days + leave_days) != 7:
                            reason = ('You can allocate 7 days for CCL Leave for %s Employee') % (emp.name)
                            reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                            emp_ids.append(emp.id)
#                             raise ValidationError(_('Warning \n You can allocate 7 days for CCL Leave for %s Employee') % (emp.name))
                    if not emp.singaporean:
                        if to_date > temp:
                            reason = ('Child should below 7 year old, of %s Employee') % (emp.name)
                            reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                            emp_ids.append(emp.id)
#                             raise ValidationError(_('Warning \n Child should below 7 year old, of %s Employee') % (emp.name))
                        if int(self.no_of_days + leave_days) != 2:
                            reason = ('You can allocate 2 days for CCL Leave for %s Employee') % (emp.name)
                            reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                            emp_ids.append(emp.id)
#                             raise ValidationError(_('Warning \n You can allocate 2 days for CCL Leave for %s Employee') % (emp.name))
                else:
                    reason = ('Employee %s does not have configure Child.') % (emp.name)
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
#                     raise ValidationError(_('Warning \n Employee %s does not have configure Child.') % (emp.name))

        if self.holiday_status_id.name == 'ECCL':
            for emp in self.employee_ids:
                if emp.singaporean:
                    holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id),
                                                                  ('type', '=', 'add'),
                                                                  ('holiday_status_id', '=', self.holiday_status_id.id),
                                                                  ('hr_year_id', '=', self.fiscal_year_id.id),
                                                                  ])
                    leave_days = 0
                    for holiday in holiday_ids:
                        leave_days += holiday.number_of_days_temp

                    temp = emp.dependent_ids and emp.dependent_ids[0].birth_date
                    if temp:
                        temp = datetime.datetime.strptime(temp, DEFAULT_SERVER_DATE_FORMAT).date()
                    for dependent in emp.dependent_ids:
                        birth = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
                        if birth > temp:
                            temp = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
                    if temp:
                        to_date = datetime.datetime.strptime(fields.Date.today() + " 00:00:00", DEFAULT_SERVER_DATETIME_FORMAT).date()
                        temp7 = temp + relativedelta(years=7)
                        temp12 = temp + relativedelta(years=12)

                        if to_date <= temp7 or to_date >= temp12:
                            reason = ('Child should between 7 to 12 year old, of %s Employee') % (emp.name)
                            reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                            emp_ids.append(emp.id)
#                             raise ValidationError(_('Warning \n Child should between 7 to 12 year old, of %s Employee') % (emp.name))
                        if int(self.no_of_days + leave_days) != 2:
                            reason = ('You can allocate 2 days for CCL Leave for %s Employee') % (emp.name)
                            reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                            emp_ids.append(emp.id)
#                             raise ValidationError(_('Warning \n You can allocate 2 days for CCL Leave for %s Employee') % (emp.name))
                    else:
                        reason = ('Employee %s does not have configure Child.') % (emp.name)
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)
#                         raise ValidationError(_('Warning \n Employee %s does not have configure Child.') % (emp.name))

                else:
                    reason = ('Employee %s is not applicable for Extender Childcare Leave') % (emp.name)
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
#                     raise ValidationError(_('Warning \n Employee %s is not applicable for Extender Childcare Leave') % (emp.name))

        if self.holiday_status_id.name == 'HOL':
            for emp in self.employee_ids:
                holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id),
                                                              ('type', '=', 'add'),
                                                              ('holiday_status_id', '=', self.holiday_status_id.id),
                                                              ('hr_year_id', '=', self.fiscal_year_id.id),
                                                              ])
                leave_days = 0
                for holiday in holiday_ids:
                    leave_days += holiday.number_of_days_temp

                joining_date = datetime.datetime.strptime(emp.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
                today_date = datetime.datetime.today().date()
                if (today_date - joining_date).days <= 120:
                    if int(self.no_of_days + leave_days) > 10:
                        reason = ('You can not allocate more than 10 days for Hospitalization leave to %s Employee, due to 0-3 months experiance. Already Allocated Leave = %s.') % (emp.name, leave_days)
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)
                if (today_date - joining_date).days > 120 and (today_date - joining_date).days <= 150:
                    if int(self.no_of_days + leave_days) > 22:
                        reason = ('You can not allocate more than 22 days for Hospitalization leave to %s Employee, due to 0-3 months experiance. Already Allocated Leave = %s.') % (emp.name, leave_days)
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)
                if (today_date - joining_date).days > 150 and (today_date - joining_date).days <= 180:
                    if int(self.no_of_days + leave_days) > 34:
                        reason = ('You can not allocate more than 34 days for Hospitalization leave to %s Employee, due to 0-3 months experiance. Already Allocated Leave = %s.') % (emp.name, leave_days)
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)
                if (today_date - joining_date).days > 180:
                    if int(self.no_of_days + leave_days) > 46:
                        reason = ('You can not allocate more than 46 days for Hospitalization leave to %s Employee, due to 0-3 months experiance. Already Allocated Leave = %s.') % (emp.name, leave_days)
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)

        if self.holiday_status_id.name == 'MOL':
            for emp in self.employee_ids:
                holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id),
                                                              ('type', '=', 'add'),
                                                              ('holiday_status_id', '=', self.holiday_status_id.id),
                                                              ('hr_year_id', '=', self.fiscal_year_id.id),
                                                              ])
                leave_days = 0
                for holiday in holiday_ids:
                    leave_days += holiday.number_of_days_temp

                joining_date = datetime.datetime.strptime(emp.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
                today_date = datetime.datetime.today().date()
                if (today_date - joining_date).days <= 90:
                    reason = ('You can not allocate Medical/Sick leave to %s Employee, due to 0-3 months experiance. Already Allocated Leave = %s.') % (emp.name, leave_days)
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
                if (today_date - joining_date).days > 90 and (today_date - joining_date).days <= 120:
                    if int(self.no_of_days + leave_days) > 5:
                        reason = ('You can not allocate more than 5 days for Medical/Sick leave to %s Employee, due to 0-3 months experiance. Already Allocated Leave = %s.') % (emp.name, leave_days)
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)
                if (today_date - joining_date).days > 120 and (today_date - joining_date).days <= 150:
                    if int(self.no_of_days + leave_days) > 8:
                        reason = ('You can not allocate more than 8 days for Medical/Sick leave to %s Employee, due to 0-3 months experiance. Already Allocated Leave = %s.') % (emp.name, leave_days)
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)
                if (today_date - joining_date).days > 150 and (today_date - joining_date).days <= 180:
                    if int(self.no_of_days + leave_days) > 11:
                        reason = ('You can not allocate more than 11 days for Medical/Sick leave to %s Employee, due to 0-3 months experiance. Already Allocated Leave = %s.') % (emp.name, leave_days)
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)
                if (today_date - joining_date).days > 180:
                    if int(self.no_of_days + leave_days) > 14:
                        reason = ('You can not allocate more than 14 days for Medical/Sick leave to %s Employee, due to 0-3 months experiance. Already Allocated Leave = %s.') % (emp.name, leave_days)
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)

        if self.holiday_status_id.name == 'SPL':
            for emp in self.employee_ids:
                holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id),
                                                              ('type', '=', 'add'),
                                                              ('holiday_status_id', '=', self.holiday_status_id.id),
                                                              ('hr_year_id', '=', self.fiscal_year_id.id),
                                                              ])
                leave_days = 0
                for holiday in holiday_ids:
                    leave_days += holiday.number_of_days_temp

                joining_date = datetime.datetime.strptime(emp.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
                today_date = datetime.datetime.today().date()
                if int(self.no_of_days + leave_days) > 7:
                    reason = ('You can not allocate more than 7 days for Shared Paternity leave to %s Employee. Already Allocated Leave = %s.') % (emp.name, leave_days)
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
                if (today_date - joining_date).days < 90:
                    reason = ('Employee %s should have 3+ months experiance in same company.') % (emp.name)
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
                if emp.marital != 'married':
                    reason = ('Only Married Employee is applicable for Shared Paternity Leave')
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)

#         res = super(allocate_leave, self).allocate_leaves()
        for emp in self.employee_ids:
            if emp.gender == 'male' and self.holiday_status_id.name in ['ML16','ML15','ML8','ML4']:
                if emp.marital == 'married':
                    reason = ('Only Married Female Employee is applicable for Maternity Leave')
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
                else:
                    reason = ('Only Female Employee is applicable for Maternity Leave')
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)

            if self.holiday_status_id.name in ['PL']:
                if emp.gender == 'female':
                    reason = ('Only Male Employee is applicable for Paternity Leave')
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)
                if not emp.dependent_ids:
                    reason = ('Employee %s does not have configure Child.') % (emp.name)
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)

                if emp.dependent_ids and not emp.dependent_ids[0].singaporean:
                    reason = ('Employee %s should have singaporean Child.') % (emp.name)
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)

                temp = emp.dependent_ids and emp.dependent_ids[0].birth_date
                if temp:
                    temp = datetime.datetime.strptime(temp, DEFAULT_SERVER_DATE_FORMAT).date()
                for dependent in emp.dependent_ids:
                    birth = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
                    if birth > temp:
                        temp = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
                if temp:
                    to_date = datetime.datetime.strptime(fields.Date.today() + " 00:00:00", DEFAULT_SERVER_DATETIME_FORMAT).date()
                    temp7 = temp + relativedelta(years=7)
                    temp12 = temp + relativedelta(years=12)

                    if to_date <= temp7 or to_date >= temp12:
                        reason = ('Paternity leave only applicable Within 16 weeks from childs DOB.')
                        reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                        emp_ids.append(emp.id)

                joining_date = datetime.datetime.strptime(emp.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
                today_date = datetime.datetime.today().date()
                if (today_date - joining_date).days < 90:
                    reason = ('Employee %s should have 3+ months experiance in same company.') % (emp.name)
                    reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
                    emp_ids.append(emp.id)

            if emp.id in emp_ids:
                continue
            leave_rec = []
            if emp.leave_config_id and emp.leave_config_id.holiday_group_config_line_ids:
                for leave in emp.leave_config_id.holiday_group_config_line_ids:
                    leave_rec.append(leave.leave_type_id.id)
                if self.holiday_status_id.id in leave_rec:
                    if self.holiday_status_id.name == 'AL' and self.fiscal_year_id.code == str(datetime.datetime.today().year):
                        current_year = datetime.datetime.today().year
                        fiscal_year_id = self.env['hr.year'].search([('code', '=', str(current_year - 1))])
                        holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id), 
                                                              ('type', '=', 'add'),
                                                              ('holiday_status_id', '=', self.holiday_status_id.id),
                                                              ('hr_year_id', '=', fiscal_year_id.id),
                                                              ])
                        leave_days = 0
                        for holiday in holiday_ids:
                            leave_days += holiday.number_of_days_temp
                        if self.no_of_days == 21:
                            #if self.no_of_days > 28:
                                #need to implement the payroll condition where 50% salary of up to 21 or 7 days will be credited
#                             if self.no_of_days == 28:
#                                 continue
                            if self.no_of_days < 28:
                                self.no_of_days = self.no_of_days + (28 - leave_days)
                        if self.no_of_days == 14:
                            #if self.no_of_days > 28:
                                #need to implement the payroll condition where 50% salary of up to 21 or 7 days will be credited
#                             if self.no_of_days == 14:
#                                 continue
                            if self.no_of_days < 14:
                                self.no_of_days = self.no_of_days + (14 - leave_days)
                    vals = {
                        'name' : 'Assign Default ' + str(self.holiday_status_id.name2),
                        'holiday_status_id': self.holiday_status_id.id, 
                        'type': self.type,
                        'employee_id': emp.id,
                        'number_of_days_temp': self.no_of_days,
                        'state': 'validate',
                        'holiday_type' : 'employee',
                        'hr_year_id':self.fiscal_year_id.id
#                        'start_date':self.start_date,
#                        'end_date':self.end_date,
                        }
                    self.env['hr.holidays'].create(vals)

        for data in reason_vals:
            self.env['allocate.leaves.reason'].create(data)
#         return res
        if not reason_vals:
            return True
        else:
            view_id = self.env.ref('propell_leave_allocation.view_allocate_leaves_info_form').id
            return {
                'name': _('Allocate Leaves'),
                'type': 'ir.actions.act_window',
                'res_model': 'allocate.leaves',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'res_id': res_id.id,
            }
