# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_teamleader = fields.Boolean(
        string='Is Team Leader', help='Tick if employee is team leader.')

    @api.multi
    def action_assign_user(self):
        return {
            'name': 'Assign User',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.employee.user.access.wizard',
            'target': 'new',
        }


HrEmployee()

class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, values):
        user = super(Users, self).create(values)
        name_finded = values.get('name', False)
        dup_name = self.env['hr.employee'].search([('name','=',name_finded)],limit=1)
        if len(dup_name) == 0:
            vals = {}
            vals['name'] = values.get('name', False)
            vals['work_email'] = values.get('login', False)
            # vals['user_id'] = user.id
            emp_obj = self.env['hr.employee'].create(vals)
            emp_obj.resource_id.write({'user_id':user.id})
        else:
            for emp in dup_name:
                emp.resource_id.write({'user_id': user.id})
                emp.write({'work_email': user.login})
            # user.employee_ids = [(6,0,(dup_name.ids))]
        user.partner_id.active = user.active
        if user.partner_id:
            user.partner_id.write({'email': user.login})
        return user

    @api.multi
    def write(self,values):
        users = super(Users, self).write(values)
        for record in self:
            if record.login:
                record.partner_id.email = record.login
                for emp in record.employee_ids:
                    emp.work_email = record.login
        return users

    @api.multi
    def unlink(self):
        for record in self:
            for emp in record.employee_ids:
                emp.unlink()
        res = super(Users, self).unlink()
        return res

Users()