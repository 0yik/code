from odoo import models, fields, api

class hr_contract_inherit(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        all_employee_group = self.env.ref('aikchin_modifier_access_right.all_employees_group')
        if self._uid in all_employee_group.users.ids:
            employee_ids = self.env['hr.employee'].search([('user_id', '=', self._uid)]).ids
            if domain:
                domain.append(('employee_id', 'in', employee_ids))
            else:
                domain = [('employee_id', 'in', employee_ids)]
        res = super(hr_contract_inherit, self).search_read(domain=domain, fields=fields, offset=offset,
                                                  limit=limit, order=order)
        return res

class hr_employee_inherit(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        sales_manager_group = self.env.ref('aikchin_modifier_access_right.all_employees_group')
        if self._uid in sales_manager_group.users.ids:
            if domain:
                domain.append(('user_id', '=', self._uid))
            else:
                domain = [('user_id', '=', self._uid)]
        res = super(hr_employee_inherit, self).search_read(domain=domain, fields=fields, offset=offset,
                                                  limit=limit, order=order)
        return res

class hr_holidays_inherit(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        all_employee_group = self.env.ref('aikchin_modifier_access_right.all_employees_group')
        if self._uid in all_employee_group.users.ids:
            employee_ids = self.env['hr.employee'].search([('user_id', '=', self._uid)]).ids
            if domain:
                domain.append(('employee_id', 'in', employee_ids))
            else:
                domain = [('employee_id', 'in', employee_ids)]
        res = super(hr_holidays_inherit, self).search_read(domain=domain, fields=fields, offset=offset,
                                                  limit=limit, order=order)
        return res

# class hr_expense_inherit(models.Model):
#     _inherit = 'hr.expense'
#
#     @api.model
#     def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
#         all_employee_group = self.env.ref('aikchin_modifier_access_right.all_employees_group')
#         if self._uid in all_employee_group.users.ids:
#             employee_ids = self.env['hr.employee'].search([('user_id', '=', self._uid)]).ids
#             if domain:
#                 domain.append(('employee_id', 'in', employee_ids))
#             else:
#                 domain = [('employee_id', 'in', employee_ids)]
#         res = super(hr_expense_inherit, self).search_read(domain=domain, fields=fields, offset=offset,
#                                                   limit=limit, order=order)
#         return res

