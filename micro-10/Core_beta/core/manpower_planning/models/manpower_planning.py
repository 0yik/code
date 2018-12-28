# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError

class manpower_planning(models.Model):
    _name = 'manpower.planning'
    _inherit = ['mail.thread']
    _description = 'Manpower Planning'

    @api.depends('start_date','end_date')
    def _get_manpower_planning_period(self):
        for record in self:
            if record.start_date and record.end_date:
                record.manpower_planning_period = datetime.strptime(record.start_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%m-%Y') + ' - ' + datetime.strptime(record.end_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%m-%Y')

    @api.depends('manpower_planning_line_ids', 'manpower_planning_line_ids.job_id')
    def _get_job_details(self):
        for record in self:
            job_total = 0
            for line in record.manpower_planning_line_ids:
                if line.job_id:
                    job_total += 1
            record.number_of_job_position_registered = job_total

    @api.depends('manpower_planning_line_ids', 'manpower_planning_line_ids.expected_new_employees')
    def _get_employee_details(self):
        for record in self:
            employee_total = 0
            for line in record.manpower_planning_line_ids:
                if line.expected_new_employees:
                    employee_total += line.expected_new_employees
            record.total_employees_targeted = employee_total

    @api.depends('manpower_planning_line_ids', 'manpower_planning_line_ids.total_of_basic_salary_budgeted')
    def _get_budget_details(self):
        for record in self:
            budget_total = 0.00
            for line in record.manpower_planning_line_ids:
                if line.total_of_basic_salary_budgeted:
                    budget_total += line.total_of_basic_salary_budgeted
            record.total_salary_budgeted = budget_total

    name = fields.Char('Manpower Planning Name', track_visibility='onchange')
    start_date = fields.Date('Manpower Planning Period', track_visibility='onchange')
    end_date = fields.Date('End Date', track_visibility='onchange')
    manpower_planning_line_ids = fields.One2many('manpower.planning.line', 'manpower_planning_id', string='Manpower Planning Lines')
    number_of_job_position_registered = fields.Integer(compute='_get_job_details', string='Number of Job Position Registered', store=True)
    total_employees_targeted = fields.Integer(compute='_get_employee_details', string='Total Employees Targeted', store=True)
    total_salary_budgeted = fields.Float(compute='_get_budget_details', string='Total Salary Budgeted', store=True)
    manpower_planning_period = fields.Char(compute='_get_manpower_planning_period', string='Manpower Planning Period', store=True)
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')], default='draft', string='Status', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company')
    address_id = fields.Many2one('res.partner', string='Job Location')

    @api.multi
    def manpower_draft_confirmed(self):
        self.write({'state': 'confirmed'})
        return True

    @api.multi
    def manpower_confirmed_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def unlink(self):
        for manpower in self:
            if manpower.state == 'confirmed':
                raise UserError(_('You cannot delete a document which is confirmed. You should set to draft instead.'))
        return super(manpower_planning, self).unlink()

manpower_planning()

class manpower_planning_line(models.Model):
    _name = 'manpower.planning.line'
    _description = 'Manpower Planning Line'

    @api.depends('job_id')
    def _get_resigned_employees(self):
        for record in self:
            if record.job_id:
                record.employee_resigned = self.env['hr.employee'].search_count([('job_id', '=', record.job_id.id), ('cessation_date', '>=', record.manpower_planning_id.start_date), ('cessation_date', '<=', record.manpower_planning_id.end_date)])
            else:
                record.employee_resigned = 0

    @api.depends('job_id')
    def _get_average_wage(self):
        for record in self:
            contract_ids = self.env['hr.contract'].search([('active_employee', '=', True),('job_id', '=', record.job_id.id)])
            if contract_ids:
                total_contract_wage = 0.00
                contract_wage_count = 0.00
                for contract_id in contract_ids:
                    total_contract_wage += contract_id.wage
                    contract_wage_count += 1
                if contract_wage_count > 0.00:
                    average_wage = total_contract_wage/contract_wage_count
                    record.average_wage = average_wage

    @api.depends('job_id')
    def _get_percentage_recruited(self):
        for record in self:
            if record.expected_new_employees > 0:
                percentage = record.hired_employees/record.expected_new_employees
                record.percentage_recruited = float(percentage) * 100

    @api.depends('job_id')
    def _get_total_basic_salary_given(self):
        for record in self:
            contract_ids = self.env['hr.contract'].search([('active_employee', '=', True), ('job_id', '=', record.job_id.id)])
            if contract_ids:
                total_contract_wage = 0.00
                for contract_id in contract_ids:
                    total_contract_wage += contract_id.wage
                record.total_basic_salary_given = total_contract_wage
                if record.basic_salary_budgeted > 0.00:
                    percentage = record.total_basic_salary_given/record.basic_salary_budgeted
                    record.percentage_basic_salary = float(percentage) * 100

    @api.depends('start_date', 'end_date')
    def _get_montly_turnover(self):
        for record in self:
            resigned_employee_ids = self.env['hr.employee'].search_count([('cessation_date', '>=', record.start_date),('cessation_date', '<=', record.end_date),('job_id', '=', record.job_id.id),('emp_status', '=', 'terminated')])
            if record.current_no_of_employees > 0:
                total_resigned = float(resigned_employee_ids)
                total_current_employee = float(record.current_no_of_employees)
                record.monthly_turnover = (total_resigned/total_current_employee) * 100
            else:
                record.monthly_turnover = 0.00

    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job Position')
    current_no_of_employees = fields.Integer(related='job_id.no_of_employee', string='Current Number of Employees', store=True)
    expected_new_employees = fields.Integer(related='job_id.no_of_recruitment', string='Expected New Employees', store=True)
    total_forecasted_employees = fields.Integer(related='job_id.expected_employees', string='Total Forecasted Employees', store=True)
    company_id = fields.Many2one('res.company', related='manpower_planning_id.company_id', string='Company', store=True)
    hired_employees = fields.Integer(related='job_id.no_of_hired_employee', string='Hired Employees', store=True)
    employee_resigned = fields.Integer(compute='_get_resigned_employees', string='Employee Resigned', store=True)
    average_wage = fields.Float(compute='_get_average_wage', string='Average Wage', store=True)
    total_of_basic_salary_budgeted = fields.Float('Total of Basic Salary Budgeted')
    basic_salary_budgeted = fields.Float(related='total_of_basic_salary_budgeted', string='Basic Salary Budgeted', store=True)
    manpower_planning_id = fields.Many2one('manpower.planning', string='Manpower Planning')
    state = fields.Selection(related="manpower_planning_id.state", string='Status', store=True)
    percentage_recruited = fields.Float(compute='_get_percentage_recruited', string='% Recruited', store=True)
    percentage_basic_salary = fields.Float(compute='_get_total_basic_salary_given', string='% Basic Salary Given', store=True)
    total_basic_salary_given = fields.Float(compute='_get_total_basic_salary_given', string='Total Basic Salary Given', store=True)
    start_date = fields.Date(related='manpower_planning_id.start_date', string='Start Date', store=True)
    end_date = fields.Date(related='manpower_planning_id.end_date', string='End Date', store=True)
    monthly_turnover = fields.Float(compute='_get_montly_turnover', string='Monthly Turnover %', store=True)

manpower_planning_line()