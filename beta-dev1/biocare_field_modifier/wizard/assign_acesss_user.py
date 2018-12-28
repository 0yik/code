# -*- coding: utf-8 -*-
from openerp.exceptions import Warning
from openerp import models, fields, api
from odoo import exceptions

class HrEmployeeUserAccessWizard(models.TransientModel):
    _name = 'employee.assign.user'

    notification = fields.Char('Notification')
    user_id = fields.Many2one('res.users','Users')

    @api.multi
    def action_assign_user(self):
        view_ref = self.env.ref('base.view_users_form')
        view_id = view_ref and view_ref.id or False,
        return {
            'name': 'Assign Access For User',
            'res_id': self.user_id.id,
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'res.users',
            'view_id':view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

HrEmployeeUserAccessWizard()