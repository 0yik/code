# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta

class MilestoneToDoList(models.Model):
    _inherit = 'milestone.todo.list'


    @api.depends('milestone_id.due_date','days')
    def calculate_date(self):
        for milestone in self:
            if milestone.milestone_id and milestone.milestone_id.due_date:
                days = int(milestone.days)
                if int(days) > 0:
                    task_date = datetime.strptime(milestone.milestone_id.due_date,"%Y-%m-%d")
                    milestone.task_date = (task_date + relativedelta(days=days)).strftime("%Y-%m-%d")
                else:
                    task_date = datetime.strptime(milestone.milestone_id.due_date,"%Y-%m-%d")
                    milestone.task_date = (task_date + relativedelta(days=days)).strftime("%Y-%m-%d")

    days = fields.Integer('Days')
    task_date = fields.Date(string="Task Date", compute='calculate_date')
