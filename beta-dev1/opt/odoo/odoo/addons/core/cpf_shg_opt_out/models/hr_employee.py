# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    opt_out_cpf_shg = fields.Boolean('Opt Out CPF SHG', help="Ticked the  “Opt Out CPF SHG” checkbox if you want to opt out from CPF Contributions to Self-Help Groups (SHGs).")


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def compute_sheet(self):
        result = super(hr_payslip, self).compute_sheet()
        hr_payslip_line_obj = self.env['hr.payslip.line'].sudo()
        for payslip in self:
            net_salary = hr_payslip_line_obj.search(
                [('slip_id', '=', payslip.id), ('category_id.code', '=', 'NET')])
            employee = payslip.contract_id and payslip.contract_id.employee_id or False
            if employee and employee.opt_out_cpf_shg:
                for one_line in hr_payslip_line_obj.search(
                        [('slip_id', '=', payslip.id), ('salary_rule_id.race_id', '!=', False)]):
                    net_salary.amount = net_salary.amount + one_line.amount
                    one_line.sudo().unlink()
        return result

