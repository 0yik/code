from datetime import datetime

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Good'),
    ('2', 'Very Good'),
    ('3', 'Excellent')
]

class Applicant(models.Model):
    _inherit = "hr.applicant"

    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            address_id = contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({'name': applicant.partner_name or contact_name,
                                                           'join_date': datetime.today().date(),
                                                           'job_id': applicant.job_id.id,
                                                           'address_home_id': address_id,
                                                           'department_id': applicant.department_id.id or False,
                                                           'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                                           'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                                                           'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_(
                        'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        dict_act_window = {
            'type': 'ir.actions.act_window',
            'name': 'hr_contract.act_hr_employee_2_hr_contract',
            'res_model': 'hr.contract',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'self',
        }
        if employee:
            user_id = self.env['res.users'].search([('name', '=', employee.name)], limit=1)
            if not user_id:
                user_id = self.env['res.users'].create({'name': employee.name, 'login': employee.name})
                employee.address_home_id = user_id.partner_id.id
                employee.user_check_tick = True
            dict_act_window['context'] = {'employee_id': employee.id,
                                          'user_id': user_id.id
                                          }
        return dict_act_window