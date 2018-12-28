from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit='res.users'
    
    @api.multi
    @api.depends('groups_id')
    def _check_for_developer_group(self):
        ir_model_data = self.env['ir.model.data']
        group_id = ir_model_data.get_object_reference('developer_task', 'group_project_developer_access')
        if group_id:
            group_id = self.env['res.groups'].sudo().browse(group_id[1])
            for record in self:            
                record.has_developer_group = record.id in map(int,group_id.users)
        else:
            for record in self:
                record.has_developer_group = False
    
    has_developer_group = fields.Boolean(compute="_check_for_developer_group",string="Has Developer Group",
                                         help="Indicates that Developer group has assigned in user or not.",store=True
                                         )