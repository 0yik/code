# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class Milestone(models.Model):
    _inherit = 'mail.thread'

    _name = 'milestone.milestone'
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')
    bridal_specialist = fields.Many2one('hr.employee', string="Specialist")
    collect = fields.Float(string='Collect (%)')
    collect_payment = fields.Boolean('Collect Payment')
    due_date = fields.Date('Due Date')
    sequence = fields.Integer('Sequence')
    complete = fields.Boolean('Milestone Completed')
    category_id = fields.Many2many('res.partner.category', string='Tags')
    pre_appointment_lines = fields.One2many('milestone.todo.list', 'milestone_id', domain=[('todo_type', '=', 'pre')], copy=True)
    during_appointment_lines = fields.One2many('milestone.todo.list', 'milestone_id', domain=[('todo_type', '=', 'during')], copy=True)
    post_appointment_lines = fields.One2many('milestone.todo.list', 'milestone_id', domain=[('todo_type', '=', 'post')], copy=True)
    notes = fields.Text('Additional Notes/Comments')
    is_tmpl = fields.Boolean('Is a Template', default=False)