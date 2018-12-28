# -*- coding: utf-8 -*-
from openerp.exceptions import Warning
from openerp import models, fields, api


class HrEmployeeUserAccessWizard(models.TransientModel):
    _name = 'hr.employee.user.access.wizard'

    @api.multi
    def create_users(self):
        active_ids = self._context.get('active_ids')
        for emp in self.env['hr.employee'].browse(active_ids):
            groups_id = []
            if emp.user_id:
                raise Warning("%s has already been assigned as an User !" % emp.name)
            if not emp.work_email:
                raise Warning("Please enter the WorkEmail!")

            # groups_id = self.env['hr.job.res.groups'].search([('job_id', '=', emp.job_id.id)]).groups_id
            vals = {
                'name': emp.name,
                'login': emp.work_email,
                # 'groups_id': [(4, gid.id) for gid in groups_id],
            }
            user = self.env['res.users'].sudo().create(vals)
            emp.resource_id.write({'user_id': user.id})
            user.partner_id.write({'email': emp.work_email})
            notification = "Please set the Access rights (Team Leader/Worker) for user %s"%user.name
            return {
                'name': 'Assign Access For User',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'employee.assign.user',
                'target': 'new',
                'context':{'default_notification':notification,'default_user_id':user.id}
            }

HrEmployeeUserAccessWizard()