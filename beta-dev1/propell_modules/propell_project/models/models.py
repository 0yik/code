# -*- coding: utf-8 -*-

from odoo import models, fields, api


class project_project(models.Model):
    _inherit = 'project.project'

    @api.model
    def _default_user_id(self):
        return [(4, self.env.uid)]

    # supervisior_id = fields.Many2one("res.users", "Supervisor")
    supervisor_id = fields.Many2many("res.users", 'project_supervisor_rel', 'project_id', 'supervisor_id',
                                     string="Supervisor")
    teammember_line = fields.One2many("project.teammember", "project_id", string="Team Member")
    user_id = fields.Many2many('res.users', 'project_user_rel', 'project_id', 'user_id',
                               string='Project Manager', default=_default_user_id)


class project_teammember(models.Model):
    _name = 'project.teammember'

    project_id = fields.Many2one('project.project')
    team_member = fields.Many2many('res.users')
    role = fields.Char('Roles')


class Task(models.Model):
    _inherit = "project.task"

    manager_id = fields.Many2many('res.users', 'task_manager_rel', 'task_id', 'manager_id', string='Project Manager',
                                  related='project_id.user_id', readonly=True)
