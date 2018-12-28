from odoo import fields, models, api, exceptions
from odoo import SUPERUSER_ID


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):

        only_see_own_employee_group_id = self.env.ref('beumer_modifier_access_right.only_see_own_employee')
        if self._uid in only_see_own_employee_group_id.users.ids:
            if domain:
                domain.append(('user_id', '=', self._uid))
            else:
                domain = [('user_id', '=', self._uid)]
        res = super(hr_employee, self).search_read(domain=domain, fields=fields, offset=offset,
                                                   limit=limit, order=order)
        return res

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        ids = []
        hr_executive_group = self.env.ref('beumer_modifier_access_right.hr_executive_group')
        if self._uid in hr_executive_group.users.ids and self._uid != SUPERUSER_ID:
            employee_tags_ids = self.env['res.users'].browse(self._uid).employee_tags_ids
            for employee_tags_id in employee_tags_ids:
                employee_ids = self.env['hr.employee'].search([])
                for employee_id in employee_ids:
                    if employee_tags_id.id in employee_id.category_ids.ids:
                        ids.append(employee_id.id)
            if domain:
                domain.append(('employee_id', 'in', ids))
            else:
                domain = [('employee_id', 'in', ids)]
        res = super(hr_contract, self).search_read(domain=domain, fields=fields, offset=offset,
                                                   limit=limit, order=order)

        return res

class hr_team(models.Model):
    _inherit = 'team.configuration'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        ids = []
        hr_executive_group = self.env.ref('beumer_modifier_access_right.hr_executive_group')
        if self._uid in hr_executive_group.users.ids and self._uid != SUPERUSER_ID:
            employee_tags_ids = self.env['res.users'].browse(self._uid).employee_tags_ids
            for employee_tags_id in employee_tags_ids:
                employee_ids = self.env['hr.employee'].search([])
                for employee_id in employee_ids:
                    if employee_tags_id.id in employee_id.category_ids.ids:
                        ids.append(employee_id.id)
            team_ids = []
            for id in ids:
                teams = self.search([])
                for team in teams:
                    employee = []
                    for employee_id in team.employee_ids:
                        if employee_id.employee_id:
                            employee.append(employee_id.employee_id.id)
                    if id in employee:
                        team_ids.append(team.id)
                        break
            if domain:
                domain.append(('id', 'in', team_ids))
            else:
                domain = [('id', 'in', team_ids)]
        res = super(hr_team, self).search_read(domain=domain, fields=fields, offset=offset,
                                                   limit=limit, order=order)

        return res