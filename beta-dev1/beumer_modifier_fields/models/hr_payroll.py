from odoo import models,api,fields

class hr_payroll(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        # action_id = self.env.ref('hr_holidays.open_company_allocation').id
        # if self._context.get('params') and self._context.get('params').get('action') and action_id == self._context.get(
        #         'params').get('action'):
        cfo_group_id = self.env.ref('beumer_modifier_access_right.cfo_group')
        hr_manager_group_id = self.env.ref('beumer_modifier_access_right.hr_manager_group')
        epayroll_admin_group_id = self.env.ref('beumer_modifier_access_right.payroll_admin_group')
        if self._uid not in cfo_group_id.users.ids and self._uid not in hr_manager_group_id.users.ids and self._uid not in epayroll_admin_group_id.users.ids:
            employee_ids = self.env['hr.employee'].search([('user_id','=',self._uid)]).ids
            if domain:
                domain.append(('employee_id', 'in', employee_ids))
            else:
                domain = [('employee_id', 'in', employee_ids)]
        res = super(hr_payroll, self).search_read(domain=domain, fields=fields, offset=offset,
                                                   limit=limit, order=order)
        return res
