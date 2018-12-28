from odoo import api, fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    leave_group_rights_id = fields.Many2one('res.groups', string="Leave Rights Group", domain=lambda self: [("category_id", "=", self.env.ref( "propell_modifier_hierarchy.group_leave_approval_hierarchy").id)])

    # @api.onchange('leave_group_rights_id')
    # def set_groups(self):
    # 	print dir(self)
    # 	print self._origin.id
    #     print "pppppp",self.leave_group_rights_id.id