# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class MilestoneTemplate(models.Model):
    _name = 'milestone.template'

    name = fields.Char('Name')
    is_actived = fields.Boolean('Active')
    gowns = fields.Integer(string='Gown')
    suites = fields.Integer(string='Suit')
    dresses = fields.Integer(string='Dress')
    bouquets = fields.Integer(string='Bouquet')
    milestone_lines = fields.One2many('milestone.template.line', 'milestone_tmpl_id')


class MilestoneTemplateLine(models.Model):
    _name = "milestone.template.line"
    _rec_name = "milestone_id"

    milestone_id = fields.Many2one('milestone.milestone', string="Milestone")
    sequence = fields.Integer(string='Sequence', related="milestone_id.sequence")
    milestone_tmpl_id = fields.Many2one('milestone.template', string="Milestone Template ID")
