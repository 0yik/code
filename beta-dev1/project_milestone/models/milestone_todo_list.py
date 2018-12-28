# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class MilestoneToDoList(models.Model):
    _name = 'milestone.todo.list'

    milestone_id = fields.Many2one('milestone.milestone', string='Milestone', ondelete="cascade")
    task_date = fields.Date(string="Task Date")
    vendor_ids = fields.Many2many('res.partner', string='Vendor')
    todo_type = fields.Selection([
    		('pre', 'Pre Appointment'),
    		('during', 'During Appointment'),
    		('post', 'Post Appointment')])
    complete = fields.Boolean()
    name = fields.Char('Tasks')