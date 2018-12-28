import datetime
import dateutil
import time
from datetime import date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, AccessError, ValidationError

class Dependets(models.Model):
    _inherit = 'dependents'

    @api.multi
    def allocate_default_leaves(self, dependent):
        for config in dependent.employee_id.leave_config_id.holiday_group_config_line_ids:
#           Check for the Maternity Leave
            if config.maternity_leave and dependent.employee_id.country_id and dependent.employee_id.gender=='female':
                line = self.env['maternity.leave'].search([('config_line_id','=',config.id),('nationality_ids','in',dependent.employee_id.country_id.id),('relationship','=',dependent.relation_ship)])
                if line and line[0].relationship and dependent.employee_id.joined_year > line[0].year:
                    self.create_holiday(config, dependent, line, leave_type='maternity_leave')
            if config.childcare_leave and dependent.employee_id.gender=='female':
                line = self.env['childcare.leave'].search([('config_line_id', '=', config.id),('nationality_ids', 'in', dependent.nationality.id)])
                if line:
                    now = datetime.datetime.utcnow().date()
                    age = dateutil.relativedelta.relativedelta(now, datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT))
                    if line and age.years <= line.age and dependent.employee_id.joined_year >= line.year:
                        self.create_holiday(config, dependent, line, leave_type='childcare_leave')
            if config.ext_childcare_leave and dependent.employee_id.gender=='female':
                dependents = dependent.search([('employee_id', '=', dependent.employee_id.id)])
                latest_birth_date = max([datetime.datetime.strptime(dep.birth_date,DEFAULT_SERVER_DATE_FORMAT) for dep in dependents])
                line = self.env['extended.childcare.leave'].search([('config_line_id', '=', config.id),('nationality_ids', 'in', dependent.nationality.id)])
                latest_year = datetime.datetime.today().year - latest_birth_date.year
                if line and latest_year >= line.age_from and latest_year <= line.age_to and dependent.employee_id.joined_year >= line.year:
                    self.create_holiday(config, dependent, line, leave_type='extended_childcare_leave')
            if config.paternity_leave and dependent.employee_id.gender=='male':
                line = self.env['paternity.leave'].search([('config_line_id', '=', config.id), ('relationship','=',dependent.relation_ship), ('nationality_ids', 'in', dependent.nationality.id)])
                now = datetime.datetime.utcnow().date()
                age = dateutil.relativedelta.relativedelta(now, datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT))
                if line and (dependent.employee_id.joined_year - age.years) >= line.year:
                    self.create_holiday(config, dependent, line, leave_type='paternity_leave')
            if config.shared_parental_leave and dependent.employee_id.gender=='male':
                line = self.env['shared.parental.leave'].search([('config_line_id', '=', config.id), ('relationship','=',dependent.relation_ship), ('nationality_ids', 'in', dependent.nationality.id)])
                now = datetime.datetime.utcnow().date()
                age = dateutil.relativedelta.relativedelta(now, datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT))
                if line and (dependent.employee_id.joined_year - age.years) >= line.year and dependent.birth_date > line.birth_date:
                    self.create_holiday(config, dependent, line, leave_type='shared_parental_leave')
            if config.unpaid_infant_care_leave:
                line = self.env['unpaid.infant.care.leave'].search([('config_line_id', '=', config.id),('nationality_ids', 'in', dependent.nationality.id)])
                now = datetime.datetime.utcnow().date()
                age = dateutil.relativedelta.relativedelta(now, datetime.datetime.strptime(dependent.birth_date, DEFAULT_SERVER_DATE_FORMAT))
                if line and age.years <= line.year and dependent.employee_id.joined_year >= line.year:
                    self.create_holiday(config, dependent, line, leave_type='unpaid_infant_care_leave')
        return True

    def create_holiday(self, config, dependent, line, leave_type=None):
        holiday_obj = self.env['hr.holidays']
        holiday_status_balance_obj = self.env['hr.holidays.status.balance']
        joined_year_obj = self.env['annual.leave.joined.year']
        contract_obj = self.env['hr.contract']
        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        year = holiday_obj.fetch_hryear(today)
        leave_used_ids = holiday_obj.search([('employee_id','=',dependent.employee_id.id), ('hr_year_id','=',year), ('holiday_status_id', '=', config.leave_type_id.id), ('type', '=', 'remove'), ('state', '=', 'validate')])
        leave_used_count = sum([leave.number_of_days_temp for leave in leave_used_ids])
        leave_assigned_ids = holiday_obj.search([('employee_id', '=', dependent.employee_id.id),('hr_year_id','=',year), ('holiday_status_id', '=', config.leave_type_id.id),('type', '=', 'add'), ('state', '=', 'validate')])
        if leave_assigned_ids:
            leave_assigned_ids.with_context({'allow_delete':True}).unlink()
        vals = {
            'name' : 'Assign Default ' + str(config.leave_type_id.name2),
            'holiday_status_id': config.leave_type_id.id, 
            'type': 'add',
            'employee_id': dependent.employee_id.id,
            'number_of_days_temp': line[0].days - leave_used_count,
            'state': 'confirm',
            'holiday_type' : 'employee',
            'hr_year_id':year,
            }
        if leave_type in ['maternity_leave']:
            vals['maternity_leave'] = True
        leave = self.env['hr.holidays'].create(vals)
        return True
