# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class hr_job(models.Model):
    _inherit = 'hr.job'

    @api.multi
    def _get_entrychecklist_count(self):
        for record in self:
            if record.education_certificate and record.salary_payslip and record.experience_certificate:
                record.entry_list_count = self.env['employee.checklist'].search_count([('document_type', '=', 'entry')])
            else:
                record.entry_list_count = 0

    education_certificate = fields.Boolean('Education Certificate')
    salary_payslip = fields.Boolean('Salary Payslip')
    experience_certificate = fields.Boolean('Experience Certificate')
    entry_list_count = fields.Integer(compute='_get_entrychecklist_count', string='Entry Checklist')

    @api.multi
    def action_view_entry_list(self):
        action = self.env.ref('employee_check_list.action_entry_checklist')
        result = action.read()[0]
        for record in self:
            if record.education_certificate and record.salary_payslip and record.experience_certificate:
                entry_checklist_ids = self.env['employee.checklist'].search([('document_type', '=', 'entry')])
                if len(entry_checklist_ids) != 1:
                    result['domain'] = "[('id', 'in', " + str(entry_checklist_ids.ids) + ")]"
                elif len(entry_checklist_ids) == 1:
                    result['views'] = [[False, 'form']]
                    result['res_id'] = entry_checklist_ids.id
        return result

hr_job()