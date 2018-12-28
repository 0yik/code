from datetime import datetime

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Applicant(models.Model):
    _inherit = "hr.applicant"

    identification_no = fields.Char("Identification No")
    previous_employment_status = fields.Char('Previous Employment Status')
    previous_employee_record = fields.Many2one('hr.employee', string="Previous Employee Record")

    @api.model
    def create(self, vals):
        applicant = super(Applicant, self).create(vals)
        contract_obj = self.env['hr.contract']
        employee = self.env['hr.employee'].search([('identification_id', '=', applicant.identification_no)])
        if employee:
            contract_ids = contract_obj.search([('employee_id', '=', employee.id)])
            if contract_ids:
                contract_id = max(contract_ids.ids)
                contract = contract_obj.browse(contract_id)
                applicant.previous_employment_status = contract.name + "(" + str(contract.date_start or '') +")"
                if contract.date_end:
                    applicant.previous_employment_status = contract.name + "(" + str(contract.date_start or '') + " to " + str(contract.date_end or '') + ")"
            applicant.previous_employee_record = employee.id
        else:
            applicant.previous_employment_status = 'None'
        return applicant