# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class hr_timesheet_sheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    # Update access right for
    def action_update_access_right(self):
        users = self.env['res.users'].search([])
        for user in users:
            if user.employee_ids:
                employee = user.employee_ids[0]
                if employee.department_id:
                    if employee.department_id.name == 'HLC' or employee.department_id.parent_id.name == 'HLC':
                        group = self.env.ref('beumer_modifier_access_right.tiemsheet_hlc_groups')
                        group.users = [(4, user.id)]
                    elif employee.department_id.name == 'O&M' or employee.department_id.parent_id.name == 'O&M':
                        group = self.env.ref('beumer_modifier_access_right.tiemsheet_om_groups')
                        group.users = [(4, user.id)]
                    else:
                        group = self.env.ref('beumer_modifier_access_right.timesheet_general_groups')
                        group.users = [(4, user.id)]

