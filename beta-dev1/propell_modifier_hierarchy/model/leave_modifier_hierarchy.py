from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    current_leave_state = fields.Selection(compute='_compute_leave_status', string="Current Leave Status",
        selection=[
            ('draft', 'New'),
            ('confirm', 'Waiting for SIC/Manager approval'),
            ('emp_approval', 'Waiting for Employee approval'),
            ('tic_approval', 'Waiting for TIC/OIC approval'),
            ('hod_approval', 'Waiting for HOD approval'),
            ('gm_approval', 'Waiting for GM approval'),
            ('ed_approval', 'Waiting for ED approval'),
            ('md_approval', 'Waiting for MD approval'),
            ('next_approval', 'Waiting for Next Manager approval'),
            ('refuse', 'Refused'), ('validate1', 'Waiting Final Approval'),
            ('validate', 'Approved'), ('cancel', 'Cancelled')
        ])
    hierarchy_id = fields.Many2one('leave.approve.hierarchy', string="Leave Approval Hierarchy")


class leave_approval_hierarchy(models.Model):
    _name = 'leave.approve.hierarchy'

    name = fields.Char('Name')
    hierarchy_line_ids = fields.One2many('leave.approve.line', 'hierarchy_id', string="Hierarchy Line Ids")
    department_id = fields.Many2one('hr.department', string="Department")
    no_approval = fields.Integer("No of Approval")

    @api.constrains('department_id', 'no_approval')
    def _check_unique_department(self):
        for obj in self:
            if obj.no_approval < 1:
                raise ValidationError(_("Warning \n Please set No of Approval more than 0."))

            hierarchy_id = self.search([('department_id', '=', obj.department_id.id), ('id', '!=', self.id)])
            if hierarchy_id:
                raise ValidationError(_("Warning \n This Department is already assigned."))

    @api.constrains('name', 'hierarchy_line_ids')
    def _check_group_hierarchy(self):
        for obj in self:
            gm_id = self.env.ref('propell_modifier_hierarchy.group_leave_gm')
            ed_id = self.env.ref('propell_modifier_hierarchy.group_leave_ed')
            md_id = self.env.ref('propell_modifier_hierarchy.group_leave_md')

            employee_ids = self.env['hr.employee'].search([('department_id', '=', obj.department_id.id)])
            user_ids = [x.user_id.id for x in employee_ids]
            for hierarchy_line in obj.hierarchy_line_ids:
                flag = True
                if gm_id == hierarchy_line.groups or ed_id == hierarchy_line.groups or md_id == hierarchy_line.groups:
                    continue
                users = self.env['res.users'].search([('leave_group_rights_id', '=', hierarchy_line.groups.id)])
                for u in user_ids:
                    if u in users.ids:
                        flag = False
                        break
                    if u == 1:
                        continue

#                 for users in hierarchy_line.groups.users:
#                     if users.id == 1:
#                         continue
#                     if users.id in user_ids:
#                         flag = False
#                         break

                if flag:
                    raise ValidationError(_("Warning \n You can not add '%s' Group because no one Employee exist in '%s' Department from this Group.") % (hierarchy_line.groups.name,obj.department_id.name))

        return True

class leave_approval_hierarchy_line(models.Model):
    _name = 'leave.approve.line'

    hierarchy_id = fields.Many2one('leave.approve.hierarchy', invisible=True)
    sequence = fields.Integer('Sequence')
    groups = fields.Many2one('res.groups', string="Groups")

    _order = "sequence desc"

    @api.onchange('groups')
    def onchange_am_check(self):
        for record in self:
            leave_categ_id = self.env.ref('propell_modifier_hierarchy.group_leave_approval_hierarchy')
            group_ids = self.env['res.groups'].search([('category_id', '=', leave_categ_id.id)])

            return {'domain': {'groups': [('id', 'in', group_ids.ids)]}}
