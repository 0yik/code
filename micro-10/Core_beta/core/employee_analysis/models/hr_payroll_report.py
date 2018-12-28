# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    active = fields.Boolean(default=True)


class EmployeeReportView(models.Model):
    _name = 'hr.employee.report.view'
    _auto = False

    name = fields.Many2one('hr.employee', string='Employee')
    department_manager_id = fields.Many2one('hr.employee', string='Department Manager')
    date_from = fields.Date(string='From')
    join_date = fields.Date(string='Date Joined')
    date_to = fields.Date(string='To')
    job_id = fields.Many2one('hr.job', string='Job Title')
    company_id = fields.Many2one('res.company', string='Company')
    department_id = fields.Many2one('hr.department', string='Department')
    net = fields.Float(string='Salary')
    emp_status = fields.Selection(selection=[('probation', 'Probation'), ('full_time', 'Full Time'),
        ('part_time', 'Part Time'), ('contract_based', 'Contract Based'),
        ('in_notice', 'In Notice'), ('internship', 'Internship'),
        ('terminated', 'Terminated'), ('outsourced', 'Outsourced'),
        ('others', 'Others')], string='Employment Status')
    # emp_status = fields.Char(string='Employment Status')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
select min(emp.id) as id,emp.id as name,emp.emp_status as emp_status,emp.join_date as join_date,
dp.id as department_id,dp.manager_id as department_manager_id,
emp.job_id as job_id, sum(hrc.wage) as net, hrc.date_start as date_from, hrc.date_end as date_to,
cmp.id as company_id from
hr_employee emp  join hr_contract hrc on (hrc.employee_id=emp.id)
full join hr_department dp on (emp.department_id=dp.id)
full join res_company cmp on (cmp.id=dp.company_id) where emp.active=true
group by emp.id, hrc.wage,dp.id,dp.manager_id,emp.job_id,hrc.date_start,hrc.date_end,cmp.id
        )""" % (self._table))
