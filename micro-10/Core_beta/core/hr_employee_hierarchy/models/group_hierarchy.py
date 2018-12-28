from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class leave_approval_hierarchy(models.Model):
    _name='leave.approve.hierarchy'

    name = fields.Char('Name')
    hierarchy_line_ids=fields.One2many('leave.approve.line','line_id',string="Hierarchy Line Ids")
    department_id = fields.Many2one('hr.department', string="Department")

    @api.constrains('department_id')
    def _check_unique_department(self):
        for obj in self:
            hierarchy_id = self.search([('department_id', '=', obj.department_id.id), ('id', '!=', self.id)])
            if hierarchy_id:
                raise ValidationError(_("Warning \n This Department is already assigned."))

    @api.constrains('name', 'hierarchy_line_ids')
    def _check_group_hierarchy(self):
        for obj in self:
            gm_id = self.env.ref('hr_employee_hierarchy.group_leave_gm')
            ed_id = self.env.ref('hr_employee_hierarchy.group_leave_ed')
            md_id = self.env.ref('hr_employee_hierarchy.group_leave_md')

            employee_ids = self.env['hr.employee'].search([('department_id', '=', obj.department_id.id)])
            user_ids = [x.user_id.id for x in employee_ids]
            for hierarchy_line in obj.hierarchy_line_ids:
                flag = True
                if gm_id == hierarchy_line.groups or ed_id == hierarchy_line.groups or md_id == hierarchy_line.groups:
                    continue
                for users in hierarchy_line.groups.users:
                    if users.id == 1:
                        continue
                    if users.id in user_ids:
                        flag = False
                        break

                if flag:
                    raise ValidationError(_("Warning \n You can not add '%s' Group because no one Employee exist in '%s' Department from this Group.") % (hierarchy_line.groups.name,obj.department_id.name))

        return True

#     _constraints = [(_check_group_hierarchy, 'Warning \n This * employee is not in * department.', [])]

class leave_approval_hierarchy_line(models.Model):
    _name='leave.approve.line'
    
    line_id=fields.Many2one('leave.approve.hierarchy', invisible=True)
    sequence=fields.Integer('Sequence')
    groups=fields.Many2one('res.groups',string="Groups")

    @api.onchange('groups')
    def onchange_am_check(self):
        for record in self:
            leave_categ_id = self.env.ref('hr_employee_hierarchy.group_leave_approval_hierarchy')
            group_ids = self.env['res.groups'].search([('category_id', '=', leave_categ_id.id)])

            return {'domain': {'groups': [('id', 'in', group_ids.ids)]}}
