# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class project_task(models.Model):
    _inherit = 'project.task'
    
    
    
    project_task_type_ids = fields.Many2many('project.task.type',
                                             'project_task_type_stages_rel',
                                             'project_id', 'task_type_id',
                                             string='Access Task Stages',
                                             domain="[('project_ids', '=', project_id)]")
    
    
    @api.multi
    def write(self, vals):
        if vals and 'stage_id' in vals.keys():
            if not self.project_task_type_ids and vals.get('stage_id'):
                raise ValidationError(_('You should not change stage. Please contact to Project Manager for approval'))
            if self.project_task_type_ids and vals.get('stage_id') not in self.project_task_type_ids.ids:
                raise ValidationError(_('You should not change stage. Please contact to Project Manager for approval'))
        res = super(project_task, self).write(vals=vals)
        return res
    
    