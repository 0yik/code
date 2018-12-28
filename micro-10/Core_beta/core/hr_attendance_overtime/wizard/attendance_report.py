# -*- coding: utf-8 -*-

from odoo import models, fields


class EmployeeAttendanceReport(models.TransientModel):
    _name = 'attendance.report'

    select_emp_dep = fields.Selection([('employee','Employees'),('department','Departments')], string="Select", default='employee')
    employees_ids = fields.Many2many('hr.employee', string="Employees")
    department_ids = fields.Many2many('hr.department', string="Departments")
    from_date = fields.Date(string="Starting Date")
    to_date = fields.Date(string="Ending Date")

    def print_attendance_report(self, data):
        """Redirects to the report with the values obtained from the wizard
        'data['form']': name of employee and the date duration"""
        data = {}
        data['form'] = self.read(['select_emp_dep', 'employees_ids', 'department_ids', 'from_date', 'to_date'])[0]
        return self.env['report'].get_action(self, 'hr_attendance_overtime.report_epmloyee_attendance', data=data)

