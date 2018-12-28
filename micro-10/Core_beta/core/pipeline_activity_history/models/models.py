# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta, date

# from odoo.odoo import tools
from odoo import tools


class pipeline_activity_history(models.Model):
    _inherit = "crm.lead"

    activity_line = fields.One2many('activity.log.line', 'lead_id', string='Activity Log Lines')


class AcivityLogLine(models.Model):
    _name = "activity.log.line"

    lead_id = fields.Many2one('crm.lead', string='Activity Log')
    next_action_id = fields.Many2one('crm.activity', string='Next Action')
    description = fields.Char(string='Description')
    summary = fields.Char(string='Summary')
    date_scheduled = fields.Date(string='Date Scheduled')
    date_updated = fields.Date(string='Date Updated')


class ActivityLog(models.TransientModel):
    _inherit = "crm.activity.log"

    @api.multi
    def action_schedule(self):
        res = super(ActivityLog, self).action_schedule()
        for log in self:
            if log.lead_id:
                Log_line = self.env['activity.log.line']
                Log_line.create({
                    'lead_id': log.lead_id.id,
                    'next_action_id': log.next_activity_id.id,
                    'summary': log.title_action or '',
                    'description': log.note or '',
                    'date_scheduled': log.date_action,
                })
        return res

    @api.multi
    def action_log(self):
        Log_line = self.env['activity.log.line']
        res = super(ActivityLog, self).action_log()
        for log in self:
            if log.lead_id:
                line_id = Log_line.search(
                    [('lead_id', '=', log.lead_id.id), ('next_action_id', '=', log.next_activity_id.id),
                     ('summary', '=', log.title_action), ('date_updated', '=', False)])
                if line_id:
                    line_id.write({'date_updated': log.date_deadline,'description': log.note})
                else:
                    Log_line.create({
                        'lead_id': log.lead_id.id,
                        'next_action_id': log.next_activity_id.id,
                        'summary': log.title_action or '',
                        'description': log.note or '',
                        'date_updated': log.date_deadline,
                    })
        return res
