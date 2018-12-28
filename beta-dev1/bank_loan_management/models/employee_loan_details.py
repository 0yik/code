from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import Warning

class employee_loan_details(models.Model):
    _inherit ='employee.loan.details'

    @api.multi
    def onchange_employee_id(self, employee):
        if not employee:
            return {'value': {'loan_policy_ids': []}}
        employee_obj = self.env['hr.employee'].browse(employee)
        policies_on_categ = []
        policies_on_empl = []
        for categ in employee_obj.category_ids:
            if categ.loan_policy:
                policies_on_categ += map(lambda x: x.id, categ.loan_policy)
        if employee_obj.loan_policy:
            policies_on_empl = map(lambda x: x.id, employee_obj.loan_policy)
        domain = [('employee_id', '=', employee), ('contract_id', '=', employee_obj.contract_id.id),
                  ('code', '=', 'GROSS')]
        line_ids = self.env['hr.payslip.line'].search(domain)
        department_id = employee_obj.department_id.id or False
        #         print 'department_id==========',department_id
        # address_id = employee_obj.address_home_id or False
        # if not address_id:
        #     raise Warning(_('There is no home/work address defined for employee : %s ') % (_(employee_obj.name)))
        # partner_id = address_id and address_id.id or False
        # if not partner_id:
        #     raise Warning(_('There is no partner defined for employee : %s ') % (_(employee_obj.name)))
        gross_amount = 0.0
        if line_ids:
            #             line = self.env['hr.payslip.line'].browse(line_ids)[0]
            line = line_ids[0]
            gross_amount = line.amount

        return {'value': {'department_id': department_id,
                          'loan_policy_ids': list(set(policies_on_categ + policies_on_empl)),
                          'employee_gross': gross_amount,
                          }}