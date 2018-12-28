# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class hr_holidays_status(models.Model):
    _inherit = 'hr.holidays.status'

    leave_type_code = fields.Char('Code')


class hr_holidays_status_balance(models.Model):
    _name = 'hr.holidays.status.balance'

    l_balance = fields.Many2one('hr.employee', 'Leave Balance')
    leave_name_l = fields.Many2one('hr.holidays.status', 'Leave Type')
    leave_code = fields.Char('Code')
    assigned_l = fields.Integer('Assigned')
    used_l = fields.Integer('Used')
    waiting_l = fields.Integer('Waiting Approval')
    balance_l = fields.Integer('Balance')
    employee_id = fields.Many2one('hr.employee', string='Employee')

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _compute_balance_of_leaves(self):
        for record in self:
            holiday_status_obj = self.env['hr.holidays.status']
            holiday_status_balance_obj = self.env['hr.holidays.status.balance']
            holiday_obj = self.env['hr.holidays']

            leave_balance_dict = {}
            leave_type_ids = holiday_status_obj.search([])
            for leave_type_id in leave_type_ids:
                leave_type_bal_ids = holiday_status_balance_obj.search([('employee_id', '=', record.id), ('leave_name_l', '=', leave_type_id.id)])

                # Getting current year
                current_date_year = datetime.now().year

                # Getting no of used leaves by an employee
                leave_used_ids = holiday_obj.search([('employee_id','=',record.id),('holiday_status_id', '=', leave_type_id.id),('type', '=', 'remove'), ('state', '=', 'validate')])
                leave_used_count = 0
                for leave_used_id in leave_used_ids:
                    used_start_date_year = datetime.strptime(leave_used_id.date_from, DEFAULT_SERVER_DATETIME_FORMAT).year
                    used_end_date_year = datetime.strptime(leave_used_id.date_to, DEFAULT_SERVER_DATETIME_FORMAT).year
                    if current_date_year == used_start_date_year and current_date_year == used_end_date_year:
                        leave_used_count += leave_used_id.number_of_days_temp

                # Getting no of leaves waiting to approve for an employee
                leave_waiting_ids = holiday_obj.search([('employee_id', '=', record.id),('holiday_status_id', '=', leave_type_id.id),('type', '=', 'remove'), ('state', '=', 'confirm')])
                leave_waiting_count = 0
                for leave_waiting_id in leave_waiting_ids:
                    waiting_start_date_year = datetime.strptime(leave_waiting_id.date_from,DEFAULT_SERVER_DATETIME_FORMAT).year
                    waiting_end_date_year = datetime.strptime(leave_waiting_id.date_to, DEFAULT_SERVER_DATETIME_FORMAT).year
                    if current_date_year == waiting_start_date_year and current_date_year == waiting_end_date_year:
                        leave_waiting_count += leave_waiting_id.number_of_days_temp

                # Getting no of leaves assigned for an employee
                leave_assigned_ids = holiday_obj.search([('employee_id', '=', record.id),('holiday_status_id', '=', leave_type_id.id),('type', '=', 'add'), ('state', '=', 'validate')])
                leave_assigned_count = 0
                for leave_assigned_id in leave_assigned_ids:
                    assigned_start_date = datetime.strptime(leave_assigned_id.hr_year_id.date_start,DEFAULT_SERVER_DATE_FORMAT)
                    assigned_end_date = datetime.strptime(leave_assigned_id.hr_year_id.date_stop,DEFAULT_SERVER_DATE_FORMAT)
                    assigned_start_date_year = datetime.strptime(str(assigned_start_date),DEFAULT_SERVER_DATETIME_FORMAT).year
                    assigned_end_date_year = datetime.strptime(str(assigned_end_date),DEFAULT_SERVER_DATETIME_FORMAT).year
                    if current_date_year == assigned_start_date_year and current_date_year == assigned_end_date_year:
                        leave_assigned_count += leave_assigned_id.number_of_days_temp

                # Calculating balance leave based on leaves used, Waiting and assigned for an employee
                leave_balance = leave_assigned_count - leave_used_count - leave_waiting_count

                leave_balance_dict['leave_name_l'] = leave_type_id.id
                leave_balance_dict['leave_code'] = leave_type_id.name
                leave_balance_dict['assigned_l'] = leave_assigned_count
                leave_balance_dict['used_l'] = leave_used_count
                leave_balance_dict['waiting_l'] = leave_waiting_count
                leave_balance_dict['balance_l'] = leave_balance
                leave_balance_dict['employee_id'] = record.id
                if leave_balance_dict['assigned_l'] > 0 or leave_balance_dict['used_l'] > 0 or leave_balance_dict['waiting_l'] > 0 or leave_balance_dict['balance_l'] > 0:
                    if leave_type_bal_ids:
                        leave_type_bal_ids.unlink()
                        holiday_status_balance_rec = holiday_status_balance_obj.create(leave_balance_dict)
                    else:
                        holiday_status_balance_rec = holiday_status_balance_obj.create(leave_balance_dict)
            record.bl_leave_type = self.env['hr.holidays.status.balance'].search([('employee_id', '=', record.id)])

    bl_leave_type = fields.One2many('hr.holidays.status.balance', compute='_compute_balance_of_leaves', string='Leave Type')