# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class ManuOrder(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_add_timesheet_cost(self):
        for rec in self:
            if rec.employee_involve_ids:
                rec.employee_involve_ids.unlink()
            if rec.mrp_plan_id:
                mrp_plan = rec.mrp_plan_id
                contract = mrp_plan.contract_id
                analytic_line = self.env['account.analytic.line'].search([('account_id','=',contract.id)])
                if analytic_line:
                    timesheets = analytic_line.mapped('sheet_id')
                    employees = timesheets.mapped('employee_id')
                    total_timesheet_cost = sum(employees.mapped('timesheet_cost'))
                    vals = {
                        'no_of_employees' : len(employees),
                        'average_pay' : total_timesheet_cost/len(employees),
                        'mrp_production_id' : self.id
                    }
                    self.env['employee.involve'].create(vals)
