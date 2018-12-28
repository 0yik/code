# -*- encoding: utf-8 -*-
from odoo import fields, api, models
from odoo.exceptions import ValidationError


class hr_contract(models.Model):

    _inherit = 'hr.contract'

    wage_to_pay = fields.Float('Wage To Pay',help='This Wage to pay value is display on payroll report')
    rate_per_hour = fields.Float('Rate per hour')
    active_employee = fields.Boolean(related='employee_id.active', string="Active Employee")

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.active_employee = self.employee_id.active

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
