# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import time

class hr_contract_inherit(models.Model):
    _inherit = 'hr.contract'

    leave_config_id = fields.Many2one('holiday.group.config', 'Leave Structure', help="Structure of Leaves")
    user_id = fields.Many2one('res.users', string='User', ondelete='cascade', index=True,
                              help="If set, action binding only applies for this user.")
    leave_all_bool = fields.Boolean('For Invisible Allocate Leave Button')

    @api.model
    def default_get(self, fields):
        result = super(hr_contract_inherit, self).default_get(fields)
        if 'employee_id' in self._context and self._context.get('employee_id'):
            result['employee_id'] = self._context.get('employee_id')
        if 'user_id' in self._context and self._context.get('user_id'):
            result['user_id'] = self._context.get('user_id')
        return result

    @api.multi
    def allocate_leaves_mannualy(self):
        '''
        This Allocate Leaves button method will assign annual leaves from 
        employee form view.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current User Id
        @param context : Standard Dictionary
        @return: Return the True
        ----------------------------------------------------------
        '''
        holiday_obj = self.env['hr.holidays']
        date_today = datetime.today()
        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        year = datetime.strptime(today, DEFAULT_SERVER_DATE_FORMAT).year
        curr_year_date = str(date_today.year) + '-01-01'
        curr_year_date = datetime.strptime(curr_year_date, DEFAULT_SERVER_DATE_FORMAT).strftime(
            DEFAULT_SERVER_DATE_FORMAT)
        curr_hr_year_id = holiday_obj.fetch_hryear(today)
        emp_leave_ids = []
        for employee in self.employee_id:
            if employee.leave_config_id.holiday_group_config_line_ids and employee.leave_config_id.holiday_group_config_line_ids.ids:
                #                for leave in employee.leave_config_id.holiday_group_config_line_ids:
                #                    emp_leave_ids.append(leave.leave_type_id.id)
                if employee.leave_config_id.holiday_group_config_line_ids:
                    for holiday in employee.leave_config_id.holiday_group_config_line_ids:
                        tot_allocation_leave = holiday.default_leave_allocation
                        if tot_allocation_leave == 0.0:
                            continue
                        if employee.user_id and employee.user_id.id == 1:
                            continue
                        add = 0.0
                        self.env.cr.execute(
                            "SELECT sum(number_of_days_temp) FROM hr_holidays where employee_id=%d and state='validate' and holiday_status_id = %d and type='add' and hr_year_id=%d" % (
                            employee.id, holiday.leave_type_id.id, curr_hr_year_id))
                        all_datas = self.env.cr.fetchone()
                        if all_datas and all_datas[0]:
                            add += all_datas[0]
                        if add > 0.0:
                            continue
                        if holiday.leave_type_id.name == 'AL' and employee.join_date > curr_year_date:
                            join_month = datetime.strptime(employee.join_date,
                                                                    DEFAULT_SERVER_DATE_FORMAT).month
                            remaining_months = 12 - int(join_month)
                            if remaining_months:
                                tot_allocation_leave = (float(tot_allocation_leave) / 12) * remaining_months
                                tot_allocation_leave = round(tot_allocation_leave)
                        if holiday.leave_type_id.name in ['PL', 'SPL'] and employee.gender != 'male':
                            continue
                        if holiday.leave_type_id.name == 'PCL' and employee.singaporean != True:
                            continue
                        if employee.leave_config_id.holiday_group_config_line_ids and employee.leave_config_id.holiday_group_config_line_ids.ids:
                            for leave in employee.leave_config_id.holiday_group_config_line_ids:
                                emp_leave_ids.append(leave.leave_type_id.id)
                            if employee.leave_config_id.holiday_group_config_line_ids:
                                if holiday.leave_type_id.name == 'AL' and employee.join_date < curr_year_date:
                                    join_year = datetime.strptime(employee.join_date,
                                                                           DEFAULT_SERVER_DATE_FORMAT).year
                                    tot_year = year - join_year
                                    if holiday.incr_leave_per_year != 0 and tot_year != 0:
                                        tot_allocation_leave += (holiday.incr_leave_per_year * tot_year)
                                if holiday.max_leave_kept != 0 and tot_allocation_leave > holiday.max_leave_kept:
                                    tot_allocation_leave = holiday.max_leave_kept
                                leave_dict = {
                                    'name': 'Assign Default ' + str(holiday.leave_type_id.name2),
                                    'employee_id': employee.id,
                                    'holiday_type': 'employee',
                                    'holiday_status_id': holiday.leave_type_id.id,
                                    'number_of_days_temp': tot_allocation_leave,
                                    'hr_year_id': curr_hr_year_id,
                                    'type': 'add',
                                    'state': 'confirm',
                                }
                                leave_id = holiday_obj.create(leave_dict)
                    self.write({'leave_all_bool': True})
                employee.write({'leave_all_bool': True})
        return True

    @api.model
    def create(self, vals):
        res = super(hr_contract_inherit, self).create(vals)
        if res.employee_id:
            res.employee_id.user_id = res.user_id
            res.employee_id.leave_config_id = res.leave_config_id
            res.employee_id.job_id = res.job_id
        return res
