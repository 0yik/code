from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
import math

class dependents(models.Model):
    _inherit = "dependents"

    singaporean = fields.Boolean(string="Child Citizenship")

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def write(self, vals):
        if vals.get('user_id', False) and len(vals):
            res = super(hr_employee, self.sudo()).write(vals)
        else:
            res = super(hr_employee, self).write(vals)
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if self._uid != 1:
            domain = [['user_id', '=', self._uid]]
            args += domain
        res = super(hr_employee, self).search(args, offset, limit, order, count=count)
        return res

# class allocate_leave_reason(models.TransientModel):
# 
#     _name = 'allocate.leaves.reason'
# 
#     allocate_leave_id = fields.Many2one('allocate.leaves')
#     employee_id = fields.Many2one('hr.employee', string="Employee")
#     reason = fields.Char(string="Reason")
# 
# class allocate_leave(models.TransientModel):
# 
#     _inherit = 'allocate.leaves'
# 
#     leave_reason_ids = fields.One2many('allocate.leaves.reason', 'allocate_leave_id')
# 
#     @api.multi
#     def allocate_leaves(self):
#         res_id = self.env['allocate.leaves'].create({})
#         reason_vals = []
#         emp_ids = []
#         if self.holiday_status_id.name == 'AL':
#             for emp in self.employee_ids:
#                 joining_date = datetime.datetime.strptime(emp.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
#                 today_date = datetime.datetime.today().date()
#                 holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id), 
#                                                               ('type', '=', 'add'), 
#                                                               ('holiday_status_id', '=', self.holiday_status_id.id),
#                                                               ('hr_year_id', '=', self.fiscal_year_id.id)
#                                                               ])
#                 leave_days = 0
#                 for holiday in holiday_ids:
#                     leave_days += holiday.number_of_days_temp
#                 if (today_date - joining_date).days < (365 * 2) and int(self.no_of_days + leave_days) != 7:
#                     if leave_days > 0.0:
#                         reason = ('The leave is already allocated to (Employee Name). If you wish to change the allocation, please refuse the allocated leave, Reset it to Draft and proceed with the changes.')
#                     else:
#                         reason = ('Leave allocation should be 7 days for the employees less than 2 years of service or for worker/technician.')
#                     reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                     emp_ids.append(emp.id)
# #                     raise ValidationError(_('Warning \n You can allocate 7 days for one year experiance Employee for %s Employee') % (emp.name))
#                 if (today_date - joining_date).days > (365 * 2) and (today_date - joining_date).days <= (365 * 8) and int(self.no_of_days + leave_days) != 14:
#                     if leave_days > 0.0:
#                         reason = ('The leave is already allocated to (Employee Name). If you wish to change the allocation, please refuse the allocated leave, Reset it to Draft and proceed with the changes.')
#                     else:
#                         reason = ('Leave allocation should be 14 days for the employees equal or greater than 2 years of service.')
#                     reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                     emp_ids.append(emp.id)
# #                     raise ValidationError(_('Warning \n You can allocate 14 days for two year experiance Employee for %s Employee') % (emp.name))
#                 if (today_date - joining_date).days > (365 * 8) and int(self.no_of_days + leave_days) != 21:
#                     if leave_days > 0.0:
#                         reason = ('The leave is already allocated to (Employee Name). If you wish to change the allocation, please refuse the allocated leave, Reset it to Draft and proceed with the changes.')
#                     else:
#                         reason = ('Leave allocation should be 21 days for the employees equal or greater than 8 years of service.')
#                     reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                     emp_ids.append(emp.id)
# #                     raise ValidationError(_('Warning \n You can allocate 21 days for eight year experiance Employee for %s Employee') % (emp.name))
# 
#         if self.holiday_status_id.name == 'CCL':
#             for emp in self.employee_ids:
#                 holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id),
#                                                               ('type', '=', 'add'),
#                                                               ('holiday_status_id', '=', self.holiday_status_id.id),
#                                                               ('hr_year_id', '=', self.fiscal_year_id.id),
#                                                               ])
#                 leave_days = 0
#                 for holiday in holiday_ids:
#                     leave_days += holiday.number_of_days_temp
# 
#                 temp = emp.dependent_ids and emp.dependent_ids[0].birth_date
#                 if temp:
#                     temp = datetime.datetime.strptime(temp, DEFAULT_SERVER_DATE_FORMAT).date()
#                 for dependent in emp.dependent_ids:
#                     birth = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
#                     if birth > temp:
#                         temp = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
#                 if temp:
#                     to_date = datetime.datetime.strptime(fields.Date.today() + " 00:00:00", DEFAULT_SERVER_DATETIME_FORMAT).date()
#                     temp = temp + relativedelta(years=7)
# 
#                     if emp.singaporean:
#                         if to_date > temp:
#                             reason = ('Child should below 7 year old, of %s Employee') % (emp.name)
#                             reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                             emp_ids.append(emp.id)
# #                             raise ValidationError(_('Warning \n Child should below 7 year old, of %s Employee') % (emp.name))
#                         if int(self.no_of_days + leave_days) != 7:
#                             reason = ('You can allocate 7 days for CCL Leave for %s Employee') % (emp.name)
#                             reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                             emp_ids.append(emp.id)
# #                             raise ValidationError(_('Warning \n You can allocate 7 days for CCL Leave for %s Employee') % (emp.name))
#                     if not emp.singaporean:
#                         if to_date > temp:
#                             reason = ('Child should below 7 year old, of %s Employee') % (emp.name)
#                             reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                             emp_ids.append(emp.id)
# #                             raise ValidationError(_('Warning \n Child should below 7 year old, of %s Employee') % (emp.name))
#                         if int(self.no_of_days + leave_days) != 2:
#                             reason = ('You can allocate 2 days for CCL Leave for %s Employee') % (emp.name)
#                             reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                             emp_ids.append(emp.id)
# #                             raise ValidationError(_('Warning \n You can allocate 2 days for CCL Leave for %s Employee') % (emp.name))
#                 else:
#                     reason = ('Employee %s does not have configure Child.') % (emp.name)
#                     reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                     emp_ids.append(emp.id)
# #                     raise ValidationError(_('Warning \n Employee %s does not have configure Child.') % (emp.name))
# 
#         if self.holiday_status_id.name == 'ECCL':
#             for emp in self.employee_ids:
#                 if emp.singaporean:
#                     holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id),
#                                                                   ('type', '=', 'add'),
#                                                                   ('holiday_status_id', '=', self.holiday_status_id.id),
#                                                                   ('hr_year_id', '=', self.fiscal_year_id.id),
#                                                                   ])
#                     leave_days = 0
#                     for holiday in holiday_ids:
#                         leave_days += holiday.number_of_days_temp
# 
#                     temp = emp.dependent_ids and emp.dependent_ids[0].birth_date
#                     if temp:
#                         temp = datetime.datetime.strptime(temp, DEFAULT_SERVER_DATE_FORMAT).date()
#                     for dependent in emp.dependent_ids:
#                         birth = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
#                         if birth > temp:
#                             temp = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
#                     if temp:
#                         to_date = datetime.datetime.strptime(fields.Date.today() + " 00:00:00", DEFAULT_SERVER_DATETIME_FORMAT).date()
#                         temp7 = temp + relativedelta(years=7)
#                         temp12 = temp + relativedelta(years=12)
# 
#                         if to_date <= temp7 or to_date >= temp12:
#                             reason = ('Child should between 7 to 12 year old, of %s Employee') % (emp.name)
#                             reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                             emp_ids.append(emp.id)
# #                             raise ValidationError(_('Warning \n Child should between 7 to 12 year old, of %s Employee') % (emp.name))
#                         if int(self.no_of_days + leave_days) != 2:
#                             reason = ('You can allocate 2 days for CCL Leave for %s Employee') % (emp.name)
#                             reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                             emp_ids.append(emp.id)
# #                             raise ValidationError(_('Warning \n You can allocate 2 days for CCL Leave for %s Employee') % (emp.name))
#                     else:
#                         reason = ('Employee %s does not have configure Child.') % (emp.name)
#                         reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                         emp_ids.append(emp.id)
# #                         raise ValidationError(_('Warning \n Employee %s does not have configure Child.') % (emp.name))
# 
#                 else:
#                     reason = ('Employee %s is not applicable for Extender Childcare Leave') % (emp.name)
#                     reason_vals.append({'employee_id': emp.id, 'reason': reason, 'allocate_leave_id': res_id.id})
#                     emp_ids.append(emp.id)
# #                     raise ValidationError(_('Warning \n Employee %s is not applicable for Extender Childcare Leave') % (emp.name))
# 
# #         res = super(allocate_leave, self).allocate_leaves()
#         for emp in self.employee_ids:
#             if emp.gender == 'male' and self.holiday_status_id.name in ['ML16','ML15','ML8','ML4']:
#                 continue
#             if emp.gender == 'female' and self.holiday_status_id.name in ['PL']:
#                 continue
#             if emp.id in emp_ids:
#                 continue
#             leave_rec = []
#             if emp.leave_config_id and emp.leave_config_id.holiday_group_config_line_ids:
#                 for leave in emp.leave_config_id.holiday_group_config_line_ids:
#                     leave_rec.append(leave.leave_type_id.id)
#                 if self.holiday_status_id.id in leave_rec:
#                     if self.holiday_status_id.name == 'AL' and self.fiscal_year_id.code == str(datetime.datetime.today().year):
#                         current_year = datetime.datetime.today().year
#                         fiscal_year_id = self.env['hr.year'].search([('code', '=', str(current_year - 1))])
#                         holiday_ids = self.env['hr.holidays'].search([('employee_id', '=', emp.id), 
#                                                               ('type', '=', 'add'),
#                                                               ('holiday_status_id', '=', self.holiday_status_id.id),
#                                                               ('hr_year_id', '=', fiscal_year_id.id),
#                                                               ])
#                         leave_days = 0
#                         for holiday in holiday_ids:
#                             leave_days += holiday.number_of_days_temp
#                         if self.no_of_days == 21:
#                             #if self.no_of_days > 28:
#                                 #need to implement the payroll condition where 50% salary of up to 21 or 7 days will be credited
#                             if self.no_of_days == 28:
#                                 continue
#                             if self.no_of_days < 28:
#                                 self.no_of_days = self.no_of_days + (28 - leave_days)
#                         if self.no_of_days == 14:
#                             #if self.no_of_days > 28:
#                                 #need to implement the payroll condition where 50% salary of up to 21 or 7 days will be credited
#                             if self.no_of_days == 14:
#                                 continue
#                             if self.no_of_days < 14:
#                                 self.no_of_days = self.no_of_days + (14 - leave_days)
#                     vals = {
#                         'name' : 'Assign Default ' + str(self.holiday_status_id.name2),
#                         'holiday_status_id': self.holiday_status_id.id, 
#                         'type': self.type,
#                         'employee_id': emp.id,
#                         'number_of_days_temp': self.no_of_days,
#                         'state': 'validate',
#                         'holiday_type' : 'employee',
#                         'hr_year_id':self.fiscal_year_id.id
# #                        'start_date':self.start_date,
# #                        'end_date':self.end_date,
#                         }
#                     self.env['hr.holidays'].create(vals)
# 
#         for data in reason_vals:
#             self.env['allocate.leaves.reason'].create(data)
# #         return res
#         if not reason_vals:
#             return True
#         else:
#             view_id = self.env.ref('sg_leave_types.view_allocate_leaves_info_form').id
#             return {
#                 'name': _('Allocate Leaves'),
#                 'type': 'ir.actions.act_window',
#                 'res_model': 'allocate.leaves',
#                 'view_mode': 'form',
#                 'view_type': 'form',
#                 'view_id': view_id,
#                 'target': 'new',
#                 'res_id': res_id.id,
#             }

class hr_holidays_status(models.Model):
    _inherit = "hr.holidays.status"

    @api.multi
    def get_days(self, employee_id):
        # need to use `dict` constructor to create a dict per id
        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        hr_year_id = self.env['hr.holidays'].fetch_hryear(today)
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
                                virtual_remaining_leaves=0)) for id in self.ids)
        holidays = self.env['hr.holidays'].search([('employee_id', '=', employee_id),
                                                   ('state', 'not in', ['draft', 'refuse', 'cancel']),
                                                   ('holiday_status_id', 'in', self.ids),
                                                   ('leave_expire', '!=', True),
                                                   ('hr_year_id','=',hr_year_id),
                                                   ])
        for holiday in holidays:
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add':
                if holiday.state == 'validate':
                    status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] += holiday.number_of_days_temp
                    if not holiday.is_recovery:
                        status_dict['max_leaves'] += holiday.number_of_days_temp
            elif holiday.type == 'remove':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= holiday.number_of_days_temp
        return result

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.depends('holiday_status_id')
    def _get_child_age(self):
        for obj in self:
            if obj.holiday_status_id and obj.holiday_status_id.name in ['CCL', 'ECCL']:
                temp = obj.employee_id.dependent_ids and obj.employee_id.dependent_ids[0].birth_date
                if temp:
                    temp = datetime.datetime.strptime(temp, DEFAULT_SERVER_DATE_FORMAT).date()
                for dependent in obj.employee_id.dependent_ids:
                    if dependent.relation_ship in ['son', 'daughter']:
                        birth = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
                        if birth > temp:
                            temp = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()

#                 birth_date = datetime.datetime.strptime(obj.child_birthdate, DEFAULT_SERVER_DATE_FORMAT).date()
                if temp:
                    to_date = datetime.datetime.strptime(fields.Date.today() + " 00:00:00", DEFAULT_SERVER_DATETIME_FORMAT).date()
                    years = relativedelta(to_date, temp).years
                    months = relativedelta(to_date, temp).months
                    obj.child_age = years + (months / 12.0)

    @api.depends('holiday_status_id')
    def _check_is_admin(self):
        for obj in self:
            if obj._uid == 1:
                obj.is_admin = True

    @api.depends('holiday_status_id')
    def _check_is_non_sp_child(self):
        for obj in self:
            for depend_id in obj.employee_id.dependent_ids:
                if depend_id.relation_ship in ['son', 'daughter']:
                    if depend_id.singaporean:
                        self.is_non_sp_child = False
                    else:
                        self.is_non_sp_child = True

    def _sg_date(self):
        date =  datetime.datetime.now()
        return date

    applicant_date = fields.Datetime(string='Date of Application', default=_sg_date)
    attachment = fields.Binary(string="Add Supporting Documents")
    attachment_name = fields.Char(string="Add Supporting Documents")
    child_age = fields.Float(string="Childs Age", compute="_get_child_age")

    attachment_gppl = fields.Binary(string="GPPL")
    attachment_gppl_name = fields.Char(string="GPPL")
    gppl_link = fields.Char(string="GPPL Link", default="https://www.profamilyleave.gov.sg/Documents/PDF/GPPL1%20(updated%2029062016).pdf")

    attachment_splas = fields.Binary(string="SPLAS")
    attachment_splas_name = fields.Char(string="SPLAS")
    attachment_spl = fields.Binary(string="SPL")
    attachment_spl_name = fields.Char(string="SPL")
    spl_link = fields.Char(string="SPL Link", default="https://www.profamilyleave.gov.sg/Documents/PDF/SPL1.pdf")

    attachment_gmpl = fields.Binary(string="GPML1")
    attachment_gmpl_name = fields.Char(string="GPML1")
    gmpl_link = fields.Char(string="GPML1 Link", default="https://www.profamilyleave.gov.sg/Documents/PDF/GPML1.pdf")

    medical_certificate = fields.Binary(string="Medical Certificate")
    medical_certificate_name = fields.Char(string="Medical Certificate")

    hospital_certificate = fields.Binary(string="Hospital Certificate")
    hospital_certificate_name = fields.Char(string="Hospital Certificate")

    death_certificate = fields.Binary(string="Death Certificate")
    death_certificate_name = fields.Char(string="Death Certificate")

    relevent_certificate = fields.Binary(string="Relevent Certificate")
    relevent_certificate_name = fields.Char(string="Relevent Certificate")

    singaporean = fields.Boolean(string="Child Citizenship")
    text = fields.Char(default="Attach agreement form from your wife (print out from SPLAS)")

    is_admin = fields.Boolean(compute="_check_is_admin")
    is_non_sp_child = fields.Boolean(compute="_check_is_non_sp_child")

    @api.constrains('holiday_status_id', 'employee_id','date_from','date_to')
    def _check_employee_leave(self):
        if self._context is None:
            self._context = {}
        for rec in self:
            if rec.type == 'remove' and rec.holiday_status_id.pre_approved ==True:
                from_date = datetime.datetime.strptime(rec.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
                qualify_date = from_date - relativedelta(days=rec.holiday_status_id.no_of_days)
                if qualify_date < datetime.datetime.today().date():
                    raise ValidationError(_('%s must be applied at least %d days in advance.' % (rec.holiday_status_id.name2, rec.holiday_status_id.no_of_days)))
        return True

    @api.multi
    def action_approve(self):
        for holiday in self:
            holiday.write({'state': 'validate'})
            holiday.action_validate()
#         if self.env.user.partner_id.id == self.next_manager_id.id or self.next_manager_id.id == False:
#             if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
#                 raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))
#             # if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
#             #     raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))
# 
#             for holiday in self:
#                 if (holiday.next_manager_user_id) and (self.env.user.id == holiday.next_manager_user_id.id):
#                     holiday.write({'next_manager_id': self.env.user.employee_ids[0].parent_id.id,
#                                    'total_approval': holiday.total_approval + 1})
#                     #             else:
#                     #                 raise UserError(_('Need to approve by '+ str(self.next_manager_user_id.name)))
# 
#                 if (holiday.no_of_approval == holiday.total_approval) or (holiday.next_manager_id.id == False):
#                     holiday.write({'state': 'validate'})
#                     holiday.action_validate()
#         else:
#             raise UserError(_('Only %s can approve leave requests.') % self.next_manager_id.name)

    @api.multi
    def get_approval_email(self):
        email = ''
        if self.employee_id.work_email:
            email = self.employee_id.work_email
        elif self.employee_id.user_id.partner_id.email:
            email = self.employee_id.user_id.partner_id.email
        else:
            raise Warning(_(' Warning \n Email must be configured in %s Employee !') % (self.employee_id.name))
#         for employee_email in work_email:
#             email += employee_email + ','
        return email

    @api.onchange('half_day', 'date_from', 'date_to', 'holiday_status_id', 'employee_id')
    def onchange_date_from(self,date_from=False, date_to=False,half_day=False, holiday_status_id=False, employee_id=False):
        if date_from == False:
            if self.date_from and not self.half_day:
                frm_date = datetime.datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT)
                self.date_from = frm_date + relativedelta(hour=1)
                date_from = self.date_from
        if date_to == False:
            if self.date_to:
                to_date = datetime.datetime.strptime(self.date_to, DEFAULT_SERVER_DATETIME_FORMAT)
                self.date_to = to_date
                date_to = self.date_to
        if holiday_status_id == False:
            holiday_status_id = self.holiday_status_id.id
        if employee_id == False:
            employee_id = self.employee_id.id
        if half_day == False:
            half_day == False
        else:
            half_day = self.half_day
        leave_day_count = False
        if holiday_status_id and holiday_status_id != False:
            leave_day_count = self.env['hr.holidays.status'].browse(holiday_status_id).count_days_by
        if (date_from and date_to) and (date_from > date_to) and half_day == False:
            result = {'value': {}}
            date_to_with_delta = datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=4)
            result['value']['date_to'] = str(date_to_with_delta)
            return result
#             raise UserError(_('Warning!\nThe start date must be anterior to the end date.'))
        elif (date_from and date_to) and half_day == True:
            date_to = date_from
        result = {'value': {}}
        if date_from and not date_to:
            date_to_with_delta = datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            result['value']['date_to'] = str(date_to_with_delta)
        if (date_to and date_from) and (date_from <= date_to):
            if leave_day_count != False and leave_day_count == 'working_days_only':
                diff_day = self._check_holiday_to_from_dates(date_from, date_to, employee_id)
                result['value']['number_of_days_temp'] = round(math.floor(diff_day))
            else:
                diff_day = self._get_number_of_days(date_from, date_to,employee_id)
                result['value']['number_of_days_temp'] = round(math.floor(diff_day))+ 1
        else:
            result['value']['number_of_days_temp'] = 0.0
        if date_from and date_to and half_day == True:
            date_to_with_delta = datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=4)
            result['value']['date_to'] = str(date_to_with_delta)
        if self.half_day == True:
            result['value']['number_of_days_temp'] = 0.5

        return result

    @api.onchange('half_day', 'date_from', 'date_to', 'holiday_status_id', 'employee_id')
    def onchange_date_to(self,date_from=False, date_to=False,half_day=False, holiday_status_id=False, employee_id=False):
        res = super(HrHolidays, self).onchange_date_to(date_from=date_from, date_to=date_to,half_day=half_day, holiday_status_id=holiday_status_id, employee_id=employee_id)
        if self.half_day:
            if res.get('value') and res.get('value').get('number_of_days_temp'):
                res['value']['number_of_days_temp'] = res.get('value').get('number_of_days_temp') - 0.50
                if (res.get('value').get('number_of_days_temp') - 0.50) > 0.5:
                    self.am_or_pm = 'AM'
        return res

    @api.onchange('half_day', 'date_from', 'holiday_status_id','employee_id')
    def onchange_half_day(self):
        if self.half_day == True:
            if self.date_from != False:
                date_to_with_delta = datetime.datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=4)
                self.date_to = str(date_to_with_delta)
                self.number_of_days_temp = 0.50
            else:
                self.date_to = self.date_from
                self.number_of_days_temp = 0.50
        else:
            result = self.onchange_date_to(date_from=self.date_from, date_to=self.date_to,half_day=False,holiday_status_id=self.holiday_status_id.id,employee_id=self.employee_id.id)
            if self.date_from:
                df = datetime.datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(hours=9)
                self.date_to = df
            self.number_of_days_temp = result['value']['number_of_days_temp']
            self.am_or_pm = False

    @api.onchange('am_or_pm')
    def onchange_am_or_pm(self):
        if self.half_day and self.date_from and self.date_to:
            if self.am_or_pm == 'AM':
                frm_date = datetime.datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT)
                self.date_from = frm_date + relativedelta(hour=1)

                to_date = datetime.datetime.strptime(self.date_to, DEFAULT_SERVER_DATETIME_FORMAT)
                self.date_to = to_date
            if self.am_or_pm == 'PM':
                if self.number_of_days_temp > 0.5:
                    frm_date = datetime.datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT)
                    self.date_from = frm_date + relativedelta(hour=1)

                    to_date = datetime.datetime.strptime(self.date_to, DEFAULT_SERVER_DATETIME_FORMAT)
                    self.date_to = to_date
                    self.am_or_pm = 'AM'
                else:
                    frm_date = datetime.datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT)
                    self.date_from = frm_date + relativedelta(hour=6)

                    to_date = datetime.datetime.strptime(self.date_to, DEFAULT_SERVER_DATETIME_FORMAT)
                    self.date_to = to_date

    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)

        if self._context.get('off_in_lieu', False):
            if res.employee_id.leave_manager:

                temp_id = self.env['ir.model.data'].get_object_reference('sg_leave_types', 'email_temp_leave_approval')[1]
#                 ctx = self.env.context.copy() if self.env.context else {}
#                 menu_id = self.env['ir.model.data'].get_object_reference('hr_holidays', 'menu_open_allocation_holidays')[1]
#                 action_id = self.env['ir.model.data'].get_object_reference('sg_leave_types', 'open_allocation_holidays_extend')[1]
#                 base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
#                 ctx['approval_link'] = base_url + "/web?#id="+ str(res.id) +"&view_type=form&model=hr.holidays&menu_id=" + str(menu_id) + "&action=" + str(action_id)
#                 ctx.pop('default_state')
#                 self.sudo().with_context(ctx).send_email(res.id, temp_id, force_send=True)

        return res

    @api.multi
    def copy(self, default=None):
#         self.ensure_one()
# 
#         date_from = datetime.datetime.strptime(str(datetime.datetime.today().date()), '%Y-%m-%d')
#         date_to = datetime.datetime.strptime(str(datetime.datetime.today().date()), '%Y-%m-%d') + datetime.timedelta(hours=8)
# 
#         default.update({'date_from': str(date_from), 'date_to': str(date_to)})
        raise UserError(_('Sorry, you can not duplicate Leave...!'))

        return super(HrHolidays, self).copy(default)

    @api.constrains('holiday_status_id','employee_id')
    def _check_sg_maternity_leave_16_weeks(self):
        '''
        The method used to Validate for Maternity Leave.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current User Id
        @param ids : Current object Id
        @param context : Standard Dictionary
        @return : True or False
        ------------------------------------------------------
        '''
        if self._context is None:
            self._context = {}
        for rec in self:
            if rec.type == 'remove' and rec.holiday_status_id.name in ['ML16','ML15','ML8','ML4']:
                if rec.employee_id.gender == 'male':
                    raise ValidationError(_('Employee should be Female! \n This Leave is only applicable for Female !'))
                if rec.holiday_status_id.pre_approved == True:
                    if rec.employee_id and rec.employee_id.id and rec.employee_id.join_date:
                        if rec.employee_id.singaporean == True and rec.employee_id.depends_singaporean == True:
                            joining_date = datetime.datetime.strptime(rec.employee_id.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
                            qualify_date = joining_date + relativedelta(months=3)
                            if datetime.datetime.today().date() < qualify_date:
                                raise ValidationError(_('Not Qualified in Joining date! \n Employee must have worked in the company for a continuous duration of at least 3 months!'))
                            from_date = datetime.datetime.strptime(rec.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
                            two_month_date = from_date - relativedelta(months=2)
                            if two_month_date < datetime.datetime.today().date():
                                raise ValidationError(_('Warning! \n Maternity Leave request should be submitted 2 months prior to the requested date.!'))
                        else:
                            raise ValidationError(_('Warning! \n Child is not Singapore citizen!'))
                    else:
                        raise ValidationError(_('You are not able to apply Request for this Maternity leave!'))


    @api.constrains('holiday_status_id','employee_id','date_from','date_to','child_birthdate')
    def _check_paternity_leave(self):
        '''
        The method used to Validate for Paternity Leave.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current User Id
        @param ids : Current object Id
        @param context : Standard Dictionary
        @return : True or False
        ------------------------------------------------------
        '''
        if self._context is None:
            self._context = {}
        today_date = datetime.datetime.today().date()
        for rec in self:
            if rec.type == 'remove' and rec.holiday_status_id.name == 'PL':
                if rec.holiday_status_id.pre_approved == True:
                    date_from = datetime.datetime.strptime(rec.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    date_to = datetime.datetime.strptime(rec.date_to, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    if (date_to - date_from).days != 14:
                        raise ValidationError(_('Warning! \n Entitlement of 2 weeks in continuous block !'))
                    if rec.employee_id.gender == 'female':
                        raise ValidationError(_('Employee should be Male! \n This Leave is only applicable for Male !'))
                    if not rec.employee_id.dependent_ids:
                        raise ValidationError(_('No Child Depends found! \n Please Add Child Detail in Depend list for this employee Profile !'))
                    depends_ids = self.env['dependents'].search([('employee_id','=',rec.employee_id.id),('birth_date','=',rec.child_birthdate),('relation_ship','in',['son','daughter'])])
                    if len(depends_ids.ids) == 0:
                        raise ValidationError(_('No Child found! \n No Child found for the Birth date %s !'%(rec.child_birthdate)))
                    if rec.employee_id and rec.employee_id.id and rec.employee_id.singaporean == True and rec.employee_id.depends_singaporean == True and rec.employee_id.join_date:
                        joining_date = datetime.datetime.strptime(rec.employee_id.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
                        qualify_date = joining_date + relativedelta(months=3)
                        if today_date >= qualify_date:
                            child_birth_date = datetime.datetime.strptime(rec.child_birthdate, DEFAULT_SERVER_DATE_FORMAT).date()
                            from_date = datetime.datetime.strptime(rec.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
                            to_date = datetime.datetime.strptime(rec.date_to, DEFAULT_SERVER_DATETIME_FORMAT).date()
                            qualify_date = child_birth_date + relativedelta(years=1)
    #                         child_bd_week = child_birth_date.isocalendar()
                            sixteen_weeks_later = child_birth_date + relativedelta(weeks=16)
                            before_qualify_date = from_date - relativedelta(weeks=2)
#                             if to_date > qualify_date:
#                                 raise ValidationError(_('Not Qualified in Joining date! \n Employee must have worked in the company for a continuous duration of at least 3 months!'))
                            if to_date > sixteen_weeks_later:
                                raise ValidationError(_('Warning! \n Paternity leave should be taken within 16 weeks of the child\'s birth date!'))
                            if before_qualify_date < today_date:
                                raise ValidationError(_('Warning! \n Paternity Leave request should be submitted 2 weeks prior to the requested date.!'))
                        else:
                            raise ValidationError(_('Not Qualified in Joining date! \n Employee must have worked in the company for a continuous duration of at least 3 months!'))
                    else:
                        raise ValidationError(_('Warning! \n Child is not Singapore citizen!'))

            if rec.type == 'remove' and rec.holiday_status_id.name == 'SPL':
                if rec.holiday_status_id.pre_approved:
                    if not rec.employee_id.dependent_ids:
                        raise ValidationError(_('No Child Depends found! \n Please Add Child Detail in Depend list for this employee Profile !'))
                    depends_ids = self.env['dependents'].search([('employee_id', '=', rec.employee_id.id), ('relation_ship', 'in', ['son', 'daughter'])])
                    if rec.employee_id.marital != 'married':
                        raise ValidationError(_('Warning.! \n Employee should be Married !'))

                    joining_date = datetime.datetime.strptime(rec.employee_id.join_date, DEFAULT_SERVER_DATE_FORMAT).date()
                    today_date = datetime.datetime.today().date()
                    if (today_date - joining_date).days < 90:
                        raise ValidationError(_('Employee %s should have 3+ months experiance in same company.' % (rec.employee_id.name)))

                    if len(depends_ids.ids) == 0:
                        raise ValidationError(_('No Child found! \n No Child found for the Birth date %s !' % (rec.child_birthdate)))
                    from_date = datetime.datetime.strptime(rec.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    date_to = datetime.datetime.strptime(rec.date_to, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    if (date_to - from_date).days != 6:
                        raise ValidationError(_('Warning! \n Entitlement of 1 weeks in continuous block !'))

                    if rec.employee_id and rec.employee_id.id and rec.employee_id.singaporean and rec.employee_id.join_date:
                        flag = False
                        for dependent in rec.employee_id.dependent_ids:
                            if dependent.relation_ship in ['son', 'daughter']:
                                birth = datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT).date()
                                if (birth + relativedelta(years=1)) >= from_date and birth <= from_date:
                                    flag = True

#                         to_date = datetime.datetime.strptime(rec.date_to, DEFAULT_SERVER_DATETIME_FORMAT).date()
                        before_qualify_date = from_date - relativedelta(weeks=2)
                        if not flag:
                            raise ValidationError(_('Warning! \n Shared Parental leave should be taken within 1 Year of the child\'s birth date!'))
                        if before_qualify_date < today_date:
                            raise ValidationError(_('Warning! \n Shared Parental Leave request should be submitted 2 weeks prior to the requested date.!'))
                    else:
                        raise ValidationError(_('Warning! \n Child is not Singapore citizen!'))

    @api.constrains('holiday_status_id','date_from','date_to','employee_id')
    def _check_marriage_leave(self):
        '''
        The method used to Validate other compassionate leave.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current User Id
        @param ids : Current object Id
        @param context : Standard Dictionary
        @return : True or False
        ------------------------------------------------------
        '''
        if self._context is None:
            self._context = {}
        for rec in self:
            if rec.type == 'remove' and rec.holiday_status_id.name in ('MLC','ML'):
                if rec.employee_id.gender == 'female' and rec.employee_id.marital != 'married':
                    raise ValidationError(_('Employee should be Married!'))

                if rec.holiday_status_id.pre_approved == True:
                    from_date = datetime.datetime.strptime(rec.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    qualify_date = from_date - relativedelta(weeks=2)
                    if qualify_date < datetime.datetime.today().date():
                        raise ValidationError(_('Marriage Leave request should be submitted 2 weeks prior to the requested date.!'))

    @api.constrains('holiday_status_id','employee_id','date_from','date_to')
    def _check_sg_medical_opt_leave(self):
        '''
        The method used to Validate medical leave.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current User Id
        @param ids : Current object Id
        @param context : Standard Dictionary
        @return : True or False
        ------------------------------------------------------
        '''
        if self._context is None:
            self._context = {}
        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        date_today = datetime.datetime.today()
        for rec in self:
            if rec.type == 'remove' and rec.holiday_status_id.name == 'MOL':
                if rec.holiday_status_id.pre_approved == True:
                    if rec.employee_id.join_date and rec.employee_id.join_date <= today:
                        join_date = datetime.datetime.strptime(rec.employee_id.join_date, DEFAULT_SERVER_DATE_FORMAT)
                        one_year_day = join_date + relativedelta(months=12)
                        three_months = join_date + relativedelta(months=3)
                        if three_months < date_today and one_year_day > date_today:
                            med_rmv = 0.0
                            self._cr.execute("SELECT sum(number_of_days_temp) FROM hr_holidays where employee_id=%d and holiday_status_id = %d and type='remove'" % (rec.employee_id.id, rec.holiday_status_id.id))
                            all_datas = self._cr.fetchone()
                            if all_datas and all_datas[0]:
                                med_rmv += all_datas[0]
                            res_date = relativedelta(date_today ,join_date)
                            tot_month = res_date.months
                            if tot_month == 3 and med_rmv > 5:
                                raise ValidationError(_('You can not apply medical leave more than 5 days in 3 months!'))
                            elif tot_month == 4 and med_rmv > 8:
                                raise ValidationError(_('You can not apply medical leave more than 8 days in 4 months!'))
                            elif tot_month == 5 and med_rmv > 11:
                                raise ValidationError(_('You can not apply medical leave more than 11 days in 5 months!'))
                            elif tot_month >= 6 and med_rmv > 14:
                                raise ValidationError(_('You can not apply medical leave more than 14 days in one Year!'))
                        if three_months > date_today:
                            raise ValidationError(_('You are not able to apply Medical leave Request.!'))

        return {'warning': {
                'title': _('Warning'),
                'message': _('Please be reminded to attach original Medical Certificate only')
                }}

    @api.constrains('holiday_status_id','date_from','date_to')
    def _check_off_in_leave(self):
        '''
        The method used to Validate other compassionate leave.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current User Id
        @param ids : Current object Id
        @param context : Standard Dictionary
        @return : True or False
        ------------------------------------------------------
        '''
        if self._context is None:
            self._context = {}
        curr_month = datetime.datetime.today().month
        for rec in self:
            if rec.type == 'remove' and rec.holiday_status_id.name == 'OIL':
                if rec.holiday_status_id.pre_approved:
                    if rec.is_urgent:
                        raise ValidationError(_('You can not apply Urgent off in leave!'))
#                     from_date = datetime.datetime.strptime(rec.date_from, DEFAULT_SERVER_DATETIME_FORMAT).month
#                     to_date = datetime.datetime.strptime(rec.date_to, DEFAULT_SERVER_DATETIME_FORMAT).month
#                     if int(from_date) != int(curr_month) or int(to_date) != int(curr_month):
#                         raise ValidationError(_('You can apply off in leave Request for current month only!'))

    @api.onchange('holiday_status_id','employee_id')
    def on_change_leavetype(self):
        res = super(HrHolidays, self).on_change_leavetype()
        if self.employee_id:
            self.next_manager_id = self.employee_id.leave_manager.id
        if self.holiday_status_id and self.holiday_status_id.name == 'MOL':
            return {'warning': {
                    'title': _('Warning'),
                    'message': _('Please be reminded to attach original Medical Certificate only')
                    }}
        if self.holiday_status_id and self.holiday_status_id.name == 'HOL':
            return {'warning': {
                    'title': _('Warning'),
                    'message': _('Please be reminded to attach original Hospitalization Certificate only')
                    }}

        if self.holiday_status_id and self.holiday_status_id.name == 'OIL':
            return {'warning': {
                    'title': _('Warning'),
                    'message': _('Off In-Lieu cannot be used for overseas trip')
                    }}

        if self._context.get('off_in_lieu', False):
            leave_status = self.env['hr.holidays.status'].search([('name', '=', 'OIL')], limit=1)
            if leave_status:
                return {'domain': {'holiday_status_id': [('id', 'in', [leave_status.id])]}}
            else:
                return {'domain': {'holiday_status_id': [('id', 'in', [])]}}
        return res

#     @api.onchange('employee_id')
#     def onchange_employee(self):
#         res = super(HrHolidays, self).onchange_employee()
#         for record in self:
#             record.next_manager_id = record.employee_id and record.employee_id.parent_id.id or False
#             record.holiday_status_id = record.holiday_status_id and record.holiday_status_id.id or False
# 
#         if self._context.get('off_in_lieu', False):
#             leave_status = self.env['hr.holidays.status'].search([('name', '=', 'OIL')], limit=1)
#             if leave_status:
#                 return {'domain': {'holiday_status_id': [('id', 'in', [leave_status.id])]}}
#             else:
#                 return {'domain': {'holiday_status_id': [('id', 'in', [])]}}
#         return res

    @api.onchange('employee_id')
    def onchange_employee(self):

        result = {}
        leave_type_ids = self.env['hr.holidays.status'].search([])
        self.leave_config_id = False
        self.holiday_status_id = False
        result.update({'domain':{'holiday_status_id':[('id','not in',leave_type_ids.ids)]}})
        if self.employee_id and self.employee_id.id:
            self.department_id = self.employee_id.department_id
            if self.employee_id.sudo().gender:
                self.gender = self.employee_id.sudo().gender
            if self.employee_id.leave_config_id and self.employee_id.leave_config_id.id:
                self.leave_config_id = self.employee_id.leave_config_id.id
                if self.employee_id.leave_config_id.holiday_group_config_line_ids and self.employee_id.leave_config_id.holiday_group_config_line_ids.ids:
                    leave_type_list = []
                    for leave_type in self.employee_id.leave_config_id.holiday_group_config_line_ids:
                        leave_type_list.append(leave_type.leave_type_id.id)
                        result['domain'] = {'holiday_status_id':[('id','in',leave_type_list)]}
            else:
                return {'warning': {'title': 'Leave Warning', 'message': 'No Leave Structure Found! \n Please configure leave structure for current employee from employee\'s profile!'},
                        'domain':result['domain']}

        for record in self:
            record.next_manager_id = record.employee_id and record.employee_id.parent_id.id or False
            record.holiday_status_id = record.holiday_status_id and record.holiday_status_id.id or False

        if self._context.get('off_in_lieu', False):
            leave_status = self.env['hr.holidays.status'].search([('name', '=', 'OIL')], limit=1)
            if leave_status:
                return {'domain': {'holiday_status_id': [('id', 'in', [leave_status.id])]}}
            else:
                return {'domain': {'holiday_status_id': [('id', 'in', [])]}}

        return result
