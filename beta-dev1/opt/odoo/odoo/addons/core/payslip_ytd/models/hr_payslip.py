from odoo import models, fields, api
import time
from datetime import date

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    @api.depends('total_ytd_gross', 'total_ytd_bonus', 'total_ytd_cpf_employee', 'total_ytd_cpf_employer')
    def _compute_total_ytd_rules(self):
        for rec in self:
            date_from = date(date.today().year, 1, 1)
            date_to = date.today()
            line_ids = self.env['hr.payslip.line'].search([('slip_id.date_from','>=',date_from), ('slip_id.date_from','<=',date_to), ('slip_id.employee_id','=',self.employee_id.id), ('slip_id.state','=','done')])
            total_gross = 0.0
            total_bonus = 0.0
            total_cpf_employee = 0.0
            total_cpf_employer = 0.0
            for line in line_ids:
                if line.code == 'GROSS':
                    total_gross+=line.amount
                if line.code =='SC121':
                    total_bonus+=line.amount
                if line.category_id.code =='CAT_CPF_EMPLOYEE':
                    total_cpf_employee+=line.amount
                if line.category_id.code =='CAT_CPF_EMPLOYER':
                    total_cpf_employer+=line.amount
            rec.total_ytd_gross = total_gross
            rec.total_ytd_bonus = total_bonus
            rec.total_ytd_cpf_employer = total_cpf_employer
            rec.total_ytd_cpf_employee = total_cpf_employee

    total_ytd_gross = fields.Float(compute='_compute_total_ytd_rules', string='Total YTD Gross')
    total_ytd_bonus = fields.Float(compute='_compute_total_ytd_rules', string='Total YTD Bonus')
    total_ytd_cpf_employee = fields.Float(compute='_compute_total_ytd_rules', string='Total YTD CPF Employee')
    total_ytd_cpf_employer = fields.Float(compute='_compute_total_ytd_rules', string='Total YTD CPF Employer')
    ot_date_from = fields.Date(string='OT Date From')
    ot_date_to = fields.Date(string='OT Date To')
