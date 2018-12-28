from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class project_project(models.Model):
    _inherit = 'project.project'

    engineer_ids = fields.Many2many("res.users", 'project_engineer_rel', 'project_id', 'engineer_id',
                                     string="Engineers")
    allow_eng = fields.Boolean(string="Include Engineer in Leave Hierarchy")

