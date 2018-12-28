# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import math
import time

class MassLeaveDeduction(models.TransientModel):
    _name = 'mass.leave.deduction'
    _description = 'Mass Leave Deduction'

    @api.depends('date_from','date_to')
    def _get_number_of_days(self):
        for record in self:
            if record.date_from and record.date_to:
                from_dt = fields.Datetime.from_string(record.date_from)
                to_dt = fields.Datetime.from_string(record.date_to)
                time_delta = to_dt - from_dt
                record.no_of_days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)

    leave_type_id = fields.Many2one(
        comodel_name='hr.holidays.status', string='Leave Type', help='Leave Type', required=True, )
    fiscal_year = fields.Many2one(
        comodel_name='hr.year', string='HR Year', help='Fiscal Year for eg. 2018')
    no_of_days = fields.Float(compute='_get_number_of_days',
        string='No. of Days', help='Add deduction day(s).', store=True)
    employee_ids = fields.Many2many(
        comodel_name='hr.employee', string='Employees',
        help='Select employee for leave deduction.')
    reason = fields.Char(
        string='Reason', size=64,
        help='Add reason of leave deduction.', required=False, )
    date_from = fields.Datetime(string='Start Date', default=lambda *a: time.strftime('%Y-%m-%d 09:00:00'))
    date_to = fields.Datetime(string='End Date', default=lambda *a: time.strftime('%Y-%m-%d 18:00:00'))

    @api.onchange('leave_type_id')
    def onchange_holiday_status(self):
        result={}
        if self.leave_type_id:
            employees_ids = self.env['hr.employee'].search([('leave_config_id','!=',False)])
            emp_rec = []
            leave_rec = []
            for emp in employees_ids:
                for leave in emp.leave_config_id.holiday_group_config_line_ids:
                    leave_rec.append(leave.leave_type_id.id)
                    if self.leave_type_id.id in leave_rec:
                        emp_rec.append(emp.id)
            result.update({'domain':{'employee_ids':[('id', 'in', emp_rec)]}})
        return result

    @api.multi
    def create_leave_deduction(self):
        """docstring for create_leave_deduction"""
        for emp in self.employee_ids:
            leave_rec = []
            if emp.leave_config_id and emp.leave_config_id.holiday_group_config_line_ids:
                for leave in emp.leave_config_id.holiday_group_config_line_ids:
                    leave_rec.append(leave.leave_type_id.id)
            if self.leave_type_id.id in leave_rec:
                vals = {
                    'name' : self.reason,
                    'holiday_status_id': self.leave_type_id.id,
                    'type': 'remove',
                    'employee_id': emp.id,
                    'number_of_days_temp': self.no_of_days if self.no_of_days > 0.0 else 0.0,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'state': 'validate',
                    'holiday_type': 'employee',
                    'hr_year_id': self.fiscal_year and self.fiscal_year.id or False,
                }
                holiday = self.env['hr.holidays'].create(vals)
                holiday.write({'is_deducted': True})
        return True


MassLeaveDeduction()
