# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date


class ProjectIssue(models.Model):
    _inherit = 'project.issue'


    @api.multi
    def _time_count(self):
        for rec in self:
            if rec.date_start and not rec.start_stop:
                datetime_diff = datetime.now() - datetime.strptime(rec.date_start, '%Y-%m-%d %H:%M:%S')
                hrs = datetime_diff.seconds / 3600
                mins = datetime_diff.seconds % 3600 / 60
                rec.time_count = "%s:%s" % (hrs, mins)
            else:
                rec.time_count = "0.0"

    date_start = fields.Datetime('Start Time')
    date_end = fields.Datetime('Stop Time')
    start_stop = fields.Boolean(string='Start Stop', default=False)
    time_count = fields.Char(compute="_time_count", string="Working Time")
    running_work_description = fields.Char(string="Work Description")

    @api.multi
    def action_start(self):
        action_click = self.search_count([('start_stop','=',True),('user_id', '=',self.env.uid)])
        if action_click >= 1:
            raise UserError(_('You cannot start work on multiple Issue. Another Issue is already in progress.'))
        else:
            ms = _("Started by %s.") % (self.env.user.name)
            self.message_post(body=ms)
            return self.write({'date_start': datetime.now(), 'date_end': False, 'start_stop': True, 'running_work_description': self.name})

    @api.multi
    def action_stop(self):
        datetime_diff = datetime.now() - datetime.strptime(self.date_start, '%Y-%m-%d %H:%M:%S')
        m, s = divmod(datetime_diff.total_seconds(), 60)
        h, m = divmod(m, 60)
        dur_h = (_('%0*d')%(2,h))
        dur_m = (_('%0*d')%(2,m*1.677966102))
        duration = dur_h+'.'+dur_m

        if not self.project_id:
            raise UserError(_('Please select project first.'))

        if not self.running_work_description:
            raise UserError(_('Please enter work description before stopping Issue.'))

        self.write({
            'start_stop': False,
            'date_end': datetime.now(),
            'running_work_description': '',
            'date_start': False,
            'timesheet_ids': [(0, 0, {
                'name': self.running_work_description,
                'account_id': self.project_id.analytic_account_id.id,
                'unit_amount': float(duration),
                'company_id': self.env.user.company_id.id,
                'user_id': self.env.user.id,
                'date_start': self.date_start,
                'date_stop': datetime.now(),
                'project_id': self.project_id.id,
             })]
        })
        ms = _("Stopped by %s.") % (self.env.user.name)
        self.message_post(body=ms) 
        return True

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    date_start = fields.Datetime('Start Time')
    date_stop = fields.Datetime('End Time')