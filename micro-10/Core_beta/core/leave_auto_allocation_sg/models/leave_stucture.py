import datetime
import time
from datetime import date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, AccessError, ValidationError

class holiday_group_config_line(models.Model):
    _inherit = 'holiday.group.config.line'

    by_joined_year = fields.Boolean("Annual Leave by Joined Year")
    line_ids = fields.One2many('annual.leave.joined.year', 'config_line_id', string="Joined Years")
    maternity_leave = fields.Boolean("Maternity Leave")
    maternity_leave_ids = fields.One2many('maternity.leave', 'config_line_id', string="Maternity Leaves")
    childcare_leave = fields.Boolean("Childcare Leave")
    childcare_leave_ids = fields.One2many('childcare.leave', 'config_line_id', string="Childcare Leaves")
    ext_childcare_leave = fields.Boolean("Childcare Leave")
    ext_childcare_leave_ids = fields.One2many('extended.childcare.leave', 'config_line_id', string="Extended Childcare Leaves")
    paternity_leave = fields.Boolean("Paternity Leave")
    paternity_leave_ids = fields.One2many('paternity.leave', 'config_line_id', string="Paternity Leaves")
    shared_parental_leave = fields.Boolean("Shared Parental Leave")
    shared_parental_leave_ids = fields.One2many('shared.parental.leave', 'config_line_id', string="Shared Parental Leaves")
    shared_parental_leave = fields.Boolean("Shared Parental Leave")
    shared_parental_leave_ids = fields.One2many('shared.parental.leave', 'config_line_id', string="Shared Parental Leaves")
    unpaid_infant_care_leave = fields.Boolean('Unpaid Infant Care Leave')
    unpaid_infant_care_leave_ids = fields.One2many('unpaid.infant.care.leave', 'config_line_id', string="Unpaid Infant Care Leave")
    sick_leave = fields.Boolean('Sick Leave')
    sick_leave_ids = fields.One2many('sick.leave', 'config_line_id', string="Sick Leave")
    hospitalisation_leave = fields.Boolean('Hospitalisation Leave')
    hospitalisation_leave_ids = fields.One2many('hospitalisation.leave', 'config_line_id', string="Hospitalisation Leave")
    
    @api.multi
    def allocate_leave_by_joinyear(self):
        leaves_structure_ids = self.env['holiday.group.config'].search([])
        for leaves_structure in leaves_structure_ids:
            for config in leaves_structure.holiday_group_config_line_ids:
                if config.by_joined_year or config.sick_leave or config.hospitalisation_leave:
                    holiday_obj = self.env['hr.holidays']
                    holiday_status_balance_obj = self.env['hr.holidays.status.balance']
                    joined_year_obj = self.env['annual.leave.joined.year']
                    sick_leave_obj = self.env['sick.leave']
                    hospitalisation_leave_obj = self.env['hospitalisation.leave']
                    today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    year = self.env['hr.holidays'].fetch_hryear(today)
                    employees_ids = self.env['hr.employee'].search([('leave_config_id','=',config.holiday_group_config_id.id)])
                    for employee in employees_ids:
                        leave_used_ids = holiday_obj.search([('employee_id','=',employee.id), ('hr_year_id','=',year), ('holiday_status_id', '=', config.leave_type_id.id),('type', '=', 'remove'), ('state', '=', 'validate')])
                        leave_used_count = sum([leave.number_of_days_temp for leave in leave_used_ids])
                        leave_assigned_ids = holiday_obj.search([('employee_id', '=', employee.id),('hr_year_id','=',year), ('holiday_status_id', '=', config.leave_type_id.id),('type', '=', 'add'), ('state', '=', 'validate')])
                        final_year = 0
                        if config.by_joined_year:
                            lines = [line.year for line in config.line_ids]
                            lines.sort()
                            for line in lines:
                                line_obj = joined_year_obj.search([('year','=',line),('config_line_id','=',config.id)])
                                if employee.joined_year >= line:
                                    final_year = line_obj.days
                                    continue
                        if config.sick_leave:
                            lines = [line.year for line in config.sick_leave_ids]
                            lines.sort()
                            for line in lines:
                                line_obj = sick_leave_obj.search([('year','=',line),('config_line_id','=',config.id)])
                                if employee.joined_year >= line:
                                    final_year = line_obj.days
                                    continue
                        if config.hospitalisation_leave:
                            lines = [line.year for line in config.hospitalisation_leave_ids]
                            lines.sort()
                            for line in lines:
                                line_obj = hospitalisation_leave_obj.search([('year','=',line),('config_line_id','=',config.id)])
                                if employee.joined_year >= line:
                                    final_year = line_obj.days
                                    continue
                        if leave_assigned_ids:
                            leave_assigned_ids.with_context({'allow_delete':True}).unlink()
                        vals = {
                            'name' : 'Assign Default ' + str(config.leave_type_id.name2),
                            'holiday_status_id': config.leave_type_id.id, 
                            'type': 'add',
                            'employee_id': employee.id,
                            'number_of_days_temp': final_year - leave_used_count,
                            'state': 'confirm',
                            'holiday_type' : 'employee',
                            'hr_year_id':year,
                            }
                        self.env['hr.holidays'].create(vals)

class AnnualLeaveJoinedYear(models.Model):
    _name = 'annual.leave.joined.year'

    year = fields.Integer('Joined Year')
    days = fields.Integer('Default Leave Days')
    config_line_id = fields.Many2one('holiday.group.config.line', string="Line")

class MaternityLeave(models.Model):
    _name = 'maternity.leave'

    year = fields.Float('Joined Year')
    gender = fields.Selection([('male','Male'),('female','Female')], string="Gender", default='male')
    relationship = fields.Selection([('son','Son'),('daughter','Daughter')], string="Relationship")
    birth_date = fields.Date("Child's Birth Date")
    nationality_ids = fields.Many2many('res.country', 'res_country_maternity_leave', 'maternity_id', 'res_country_id', string="Child's Nationality")
    days = fields.Integer('Default Leave Days')
    config_line_id = fields.Many2one('holiday.group.config.line', string="Line")

class ChildcareLeave(models.Model):
    _name = 'childcare.leave'
    
    year = fields.Float('Joined Year')
    age = fields.Float(string="Child's Age")
    nationality_ids = fields.Many2many('res.country', 'res_country_childcare_leave', 'childcare_id', 'res_country_id', string="Child's Nationality")
    days = fields.Integer('Default Leave Days')
    config_line_id = fields.Many2one('holiday.group.config.line', string="Config")

class ExtendedChildcareLeave(models.Model):
    _name = 'extended.childcare.leave'

    year = fields.Float('Joined Year')
    age_from = fields.Float(string="Child's Age(From)")
    age_to = fields.Float(string="Child's Age(To)")
    nationality_ids = fields.Many2many('res.country', 'res_country_childcare_leave', 'ext_childcare_id', 'res_country_id', string="Child's Nationality")
    days = fields.Integer('Default Leave Days')
    config_line_id = fields.Many2one('holiday.group.config.line', string="Config")

class PaternityLeave(models.Model):
    _name = 'paternity.leave'

    year = fields.Float('Joined Year')
    gender = fields.Selection([('male','Male'),('female','Female')], string="Gender", default='male')
    relationship = fields.Selection([('son','Son'),('daughter','Daughter')], string="Relationship")
    nationality_ids = fields.Many2many('res.country', 'res_country_paternity_leave', 'pat_maternity_id', 'res_country_id', string="Child's Nationality")
    days = fields.Integer('Default Leave Days')
    config_line_id = fields.Many2one('holiday.group.config.line', string="Line")

class SharedParentalLeave(models.Model):
    _name = 'shared.parental.leave'

    year = fields.Float('Joined Year')
    gender = fields.Selection([('male','Male'),('female','Female')], string="Gender", default='male')
    marital = fields.Selection([('single','Single'),('married','Married'),('divorced','Divorced'),('widower','Widower')], string="Marital Status")
    relationship = fields.Selection([('son','Son'),('daughter','Daughter')], string="Relationship")
    nationality_ids = fields.Many2many('res.country', 'res_country_parental_leave', 'parental_id', 'res_country_id', string="Child's Nationality")
    days = fields.Integer('Default Leave Days')
    config_line_id = fields.Many2one('holiday.group.config.line', string="Line")
    birth_date = fields.Date("Child's Birth Date")

class UnpaidInfantCareLeave(models.Model):
    _name = 'unpaid.infant.care.leave'

    year = fields.Float('Joined Year')
    age = fields.Float(string="Child's Age")
    nationality_ids = fields.Many2many('res.country', 'res_country_unpaid_infant_leave', 'infant_id', 'res_country_id', string="Child's Nationality")
    days = fields.Integer('Default Leave Days')
    config_line_id = fields.Many2one('holiday.group.config.line', string="Line")

class SickLeave(models.Model):
    _name = 'sick.leave'

    year = fields.Float('Joined Year')
    days = fields.Integer('Default Leave Days')
    config_line_id = fields.Many2one('holiday.group.config.line', string="Line")

class HosptalisationLeave(models.Model):
    _name = 'hospitalisation.leave'

    year = fields.Float('Joined Year')
    days = fields.Integer('Default Leave Days')
    config_line_id = fields.Many2one('holiday.group.config.line', string="Line")

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    maternity_leave = fields.Boolean('Maternity Leave', default=False)

    @api.multi
    def unlink(self):
        if not self._context.get('allow_delete', False):
            return super(HrHolidays, self).unlink()
        return super(models.Model, self).unlink()
