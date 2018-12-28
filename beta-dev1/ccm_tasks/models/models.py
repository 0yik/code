# -*- coding: utf-8 -*-

from odoo import fields, models


class Milestone(models.Model):
    _inherit = "milestone.milestone"

    project_id = fields.Many2one('project.project')


class Project(models.Model):
    _inherit = "project.project"

    milestone_ids = fields.One2many('milestone.milestone', 'project_id', string="Milestones")
