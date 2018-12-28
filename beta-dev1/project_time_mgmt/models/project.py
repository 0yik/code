# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime

class Task(models.Model):
    _inherit = 'project.task'

    user_id = fields.Many2many('res.users', 'rel_assgned_project_task_user',
        'project_task_id', 'user_id', 'Assigned to')

    @api.model
    def create(self, vals):
        if vals.get('user_id'):
            ins_lst = []
            for ins_res in vals.get('user_id')[0][2]:
                if ins_res:
                    ins_lst.append(ins_res)
                if ins_lst:
                    vals.update({'user_id': [(6, 0, ins_lst)]})
        return super(Task, self).create(vals)


class DailyWorkJournal(models.Model):
    _name = 'daily.work.journal'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    date = fields.Date('Date', default=lambda self: fields.Datetime.now())
    work_ids = fields.One2many('daily.journal.task.work', 'journal_id', 'Work Summary')


    @api.multi
    def action_sync_timesheet(self):
        for project in self:
            for line in project.work_ids:
                project_task_id = self.env['account.analytic.line'].\
                            search([('task_id','=',line.task_id.id)])
                if project_task_id:
                    project_task_id.update({
                            'start_datetime': line.start_date,
                            'end_datetime': line.end_date,
                            'name':line.remarks
                        })
                else:
                    line.task_id.write({'timesheet_ids': [(0, 0, {
                        'project_id': line.project_id.id,
                        'task_id': line.task_id.id,
                        'start_datetime': line.start_date,
                        'end_datetime': line.end_date,
                        'name': line.remarks,
                        'user_id': line.project_id.user_id.id,
                        'unit_amount': line.durations,
                })]})
        return True



class DailyJournalTaskWork(models.Model):
    _name = 'daily.journal.task.work'

    journal_id =  fields.Many2one('daily.work.journal', 'Journal')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    project_id = fields.Many2one('project.project', 'Project', required=True)
    task_id = fields.Many2one('project.task', 'Task')
    remarks = fields.Text('Remarks')
    durations = fields.Float(compute='_get_duration', string='Duration', store=True)

    @api.one
    @api.depends('start_date', 'end_date')
    def _get_duration(self):
        """ Get the duration value between the 2 given dates. """
        start = self.start_date
        stop = self.end_date
        if start and stop:
            diff = fields.Datetime.from_string(stop) - fields.Datetime.from_string(start)
            if diff:
                self.durations = round(float(diff.days) * 24 + (float(diff.seconds) / 3600), 2)
                return self.durations
            return 0.0

    @api.one
    @api.constrains('start_date','end_date')
    def _check_days(self):
	if self.end_date <= self.start_date:
	    raise Warning(_('End date must be greater than start date'))
