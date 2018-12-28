# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class ProjectTask(models.Model):
    _inherit = 'project.task'

    state = fields.Selection([
        ('pending','Pending'),
        ('in_progress','In Progress'),
        ('complete','Completed'),
        ('cancel','Cancelled'),
    ], default='pending')

