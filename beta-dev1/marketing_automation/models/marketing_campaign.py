# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging

from datetime import timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.fields import Datetime
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class MarketingCampaign(models.Model):
    _name = 'marketing.automation.campaign'
    _description = 'Marketing Campaign'
    _inherits = {'utm.campaign': 'utm_campaign_id'}
    _order = 'create_date DESC'

    @api.model
    def create(self, values):
        activity_obj = self.env['marketing.automation.activity']
        activity_parents = []
        for activity in values.get('marketing_activity_ids', []):
            if activity and activity[0] in [0,1] and 'parent_id' in activity[2].keys() and type(activity[2]['parent_id']) is not int:
                activity_parents.append((activity[2]['name'], activity[2]['parent_id']))
                del activity[2]['parent_id']
        rec = super(MarketingCampaign, self).create(values)
        for activity_parent in activity_parents:
            activity = activity_obj.search([('campaign_id', '=', rec.id), ('name', '=', activity_parent[0])], limit=1)
            parent = activity_obj.search([('campaign_id', '=', rec.id), ('name', '=', activity_parent[1])], limit=1)
            activity.write({'parent_id': parent.id })
        return rec

    @api.multi
    def write(self, values):
        activity_obj = self.env['marketing.automation.activity']
        for rec in self:
            activity_parents = []
            for activity in values.get('marketing_activity_ids', []):
                if activity and activity[0] in [0,1] and 'parent_id' in activity[2].keys() and type(activity[2]['parent_id']) is not int:
                    activity_parents.append((activity[2]['name'], activity[2]['parent_id']))
                    del activity[2]['parent_id']
            super(MarketingCampaign, rec).write(values)
            for activity_parent in activity_parents:
                activity = activity_obj.search([('campaign_id', '=', rec.id), ('name', '=', activity_parent[0])], limit=1)
                parent = activity_obj.search([('campaign_id', '=', rec.id), ('name', '=', activity_parent[1])], limit=1)
                activity.write({'parent_id': parent.id })
        return True

    utm_campaign_id = fields.Many2one('utm.campaign', 'UTM Campaign', ondelete='cascade', required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('running', 'Running'),
        ('stopped', 'Stopped')
        ], copy=False, default='draft')
    model_id = fields.Many2one(
        'ir.model', string='Model', index=True, required=True,
        default=lambda self: self.env.ref('base.model_res_partner', raise_if_not_found=False),
        domain="[]")
    model_name = fields.Char(string='Model Name', related='model_id.model', readonly=True, store=True, default="res.partner")
    unique_field_id = fields.Many2one(
        'ir.model.fields', string='Unique Field',
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['char', 'int', 'many2one', 'text', 'selection'])]",
        help="""Used to avoid duplicates based on model field.\ne.g.
                For model 'Customers', select email field here if you don't
                want to process records which have the same email address""")
    domain = fields.Char(string='Filter', default='[]')
    
    marketing_activity_ids = fields.One2many('marketing.automation.activity', 'campaign_id', string='Activities', copy=True)
    last_sync_date = fields.Datetime(string='Last activities synchronization')
    require_sync = fields.Boolean(string="Sync of participants is required", compute='_compute_require_sync')
    
    participant_ids = fields.One2many('marketing.participant', 'campaign_id', string='Participants')
    running_participant_count = fields.Integer(string="# of active participants", compute='_compute_participants')
    completed_participant_count = fields.Integer(string="# of completed participants", compute='_compute_participants')
    total_participant_count = fields.Integer(string="# of active and completed participants", compute='_compute_participants')

    @api.depends('marketing_activity_ids.require_sync', 'last_sync_date')
    def _compute_require_sync(self):
        for campaign in self.filtered(lambda camp: camp.last_sync_date and camp.state == 'running'):
            activities_changed = campaign.marketing_activity_ids.filtered(lambda activity: activity.require_sync)
            campaign.require_sync = bool(activities_changed)

    @api.depends('participant_ids.state')
    def _compute_participants(self):
        participants_data = self.env['marketing.participant'].read_group(
            [('campaign_id', 'in', self.ids)],
            ['campaign_id', 'state'],
            ['campaign_id', 'state'], lazy=False)
        mapped_data = {campaign.id: {} for campaign in self}
        for data in participants_data:
            mapped_data[data['campaign_id'][0]][data['state']] = data['__count']
        for campaign in self:
            campaign_data = mapped_data.get(campaign.id)
            campaign.running_participant_count = campaign_data.get('running', 0)
            campaign.completed_participant_count = campaign_data.get('completed', 0)
            campaign.total_participant_count = campaign.completed_participant_count + campaign.running_participant_count

    def action_set_synchronized(self):
        self.write({'last_sync_date': Datetime.now()})
        self.mapped('marketing_activity_ids').write({'require_sync': False})

    def action_update_participants(self):
        for campaign in self:
            modified_activities = campaign.marketing_activity_ids.filtered(lambda activity: activity.require_sync)
            traces_to_reschedule = self.env['marketing.trace'].search([
                ('state', '=', 'scheduled'),
                ('activity_id', 'in', modified_activities.ids)])
            for trace in traces_to_reschedule:
                trace_offset = relativedelta(**{trace.activity_id.interval_type: trace.activity_id.interval_number})
                trigger_type = trace.activity_id.trigger_type
                if trigger_type == 'begin':
                    trace.schedule_date = Datetime.from_string(trace.participant_id.create_date) + trace_offset
                elif trigger_type in ['act', 'mail_not_open', 'mail_not_click', 'mail_not_reply'] and trace.parent_id:
                    trace.schedule_date = Datetime.from_string(trace.parent_id.schedule_date) + trace_offset
                elif trace.parent_id:
                    process_dt = trace.parent_id.statistics_ids.state_update
                    trace.schedule_date = Datetime.from_string(process_dt) + trace_offset

            created_activities = campaign.marketing_activity_ids.filtered(lambda a: a.create_date >= campaign.last_sync_date)
            for activity in created_activities:
                activity_offset = relativedelta(**{activity.interval_type: activity.interval_number})
                if activity.trigger_type == 'begin':
                    participants = self.env['marketing.participant'].search([('state', '=', 'running')])
                    for participant in participants:
                        schedule_date = Datetime.from_string(Datetime.now()) + activity_offset
                        self.env['marketing.trace'].create({
                            'activity_id': activity.id,
                            'participant_id': participant.id,
                            'schedule_date': schedule_date,
                        })
                else:
                    valid_parent_traces = self.env['marketing.trace'].search([
                        ('state', '=', 'processed'),
                        ('activity_id', '=', activity.parent_id.id)
                    ])

                    if activity.trigger_type in ['mail_not_open', 'mail_not_click', 'mail_not_reply']:
                        opposite_trigger = activity.trigger_type.replace('_not_', '_')
                        brother_traces = self.env['marketing.trace'].search([
                            ('parent_id', 'in', valid_parent_traces.ids),
                            ('trigger_type', '=', opposite_trigger),
                            ('state', '=', 'processed'),
                        ])
                        valid_parent_traces = valid_parent_traces - brother_traces.mapped('parent_id')

                    valid_parent_traces.mapped('participant_id').filtered(lambda participant: participant.state == 'completed').action_set_running()

                    for parent_trace in valid_parent_traces:
                        self.env['marketing.trace'].create({
                            'activity_id': activity.id,
                            'participant_id': parent_trace.participant_id.id,
                            'parent_id': parent_trace.id,
                            'schedule_date': Datetime.from_string(parent_trace.schedule_date) + activity_offset,
                        })

        self.action_set_synchronized()

    def action_start_campaign(self):
        if any(not campaign.marketing_activity_ids for campaign in self):
            raise ValidationError(_('You must set up at least one activity to start this campaign.'))
        self.write({'state': 'running'})

    def action_stop_campaign(self):
        self.write({'state': 'stopped'})

    def sync_participants(self, from_cron=False):
        participants = self.env['marketing.participant']
        if from_cron:
            self = self.search([('state', '=', 'running')])
        for campaign in self.filtered(lambda c: c.marketing_activity_ids):
            now = Datetime.from_string(Datetime.now())
            if not campaign.last_sync_date:
                campaign.last_sync_date = now

            RecordModel = self.env[campaign.model_name]

            participants_data = participants.search_read([('campaign_id', '=', campaign.id)], ['res_id'])
            existing_rec_ids = set([live_participant['res_id'] for live_participant in participants_data])

            record_domain = safe_eval(campaign.domain or [])

            if campaign.unique_field_id and campaign.unique_field_id.name != 'id':

                existing_records = RecordModel.read(existing_rec_ids, [campaign.unique_field_id.name])
                unique_field_vals = set([rec[campaign.unique_field_id.name] for rec in existing_records])
                unique_domain = [(campaign.unique_field_id.name, 'not in', unique_field_vals)]
                record_domain = expression.AND([unique_domain, record_domain])
            db_rec_ids = set(RecordModel.search(record_domain).ids)
            to_create = db_rec_ids - existing_rec_ids
            to_remove = existing_rec_ids - db_rec_ids

            for rec_id in to_create:
                participants |= participants.create({
                    'campaign_id': campaign.id,
                    'res_id': rec_id,
                })

            if to_remove:
                participants.search([('res_id', 'in', list(to_remove))]).action_set_unlink()

        return participants

    @api.multi
    def execute_activities(self, from_cron=False):
        if from_cron:
            self = self.search([('state', '=', 'running')])
        for campaign in self.filtered(lambda c: c.state=='running'):
            campaign.marketing_activity_ids.execute()


class MarketingActivity(models.Model):
    _name = 'marketing.automation.activity'
    _description = 'Marketing Activity'
    _inherits = {'utm.source': 'utm_source_id'}
    _order = 'interval_standardized'

    utm_source_id = fields.Many2one('utm.source', 'Source', ondelete='cascade', required=True)
    campaign_id = fields.Many2one(
        'marketing.automation.campaign', string='Campaign',
        index=True, ondelete='cascade', required=False)
    interval_number = fields.Integer(string='Send after', default=1)
    interval_type = fields.Selection([
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')], string='Delay Type',
        default='hours', required=True)
    interval_standardized = fields.Integer('Send after (in hours)', compute='_compute_interval_standardized', store=True, readonly=True)

    validity_duration = fields.Boolean('Validity Duration')
    validity_duration_number = fields.Integer(string='Valid during', default=0)
    validity_duration_type = fields.Selection([
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')],
        default='hours', required=True)

    require_sync = fields.Boolean('Require trace sync')

    domain = fields.Char(
        string='Filter',
        help='Activity will only be performed if record satisfies this domain')
    model_id = fields.Many2one('ir.model', related='campaign_id.model_id', string='Model')
    model_name = fields.Char(related='campaign_id.model_id.model', string='Model Name')

    activity_type = fields.Selection([
        ('email', 'Email'),
        ('action', 'Server Action')
        ], required=True, default='email')
    mass_mailing_id = fields.Many2one('mail.mass_mailing', string='Email Template')
    server_action_id = fields.Many2one('ir.actions.server', string='Server Action')

    parent_id = fields.Many2one(
        'marketing.automation.activity', string='Activity',
        index=True, ondelete='cascade')
    child_ids = fields.One2many('marketing.automation.activity', 'parent_id', string='Child Activities')
    trigger_type = fields.Selection([
        ('begin', 'beginning of campaign'),
        ('act', 'another activity'),
        ('mail_open', 'Mail: opened'),
        ('mail_not_open', 'Mail: not opened'),
        ('mail_reply', 'Mail: replied'),
        ('mail_not_reply', 'Mail: not replied'),
        ('mail_click', 'Mail: clicked'),
        ('mail_not_click', 'Mail: not clicked'),
        ('mail_bounce', 'Mail: bounced')], default='begin', required=True)

    trace_ids = fields.One2many('marketing.trace', 'activity_id', string='Traces')
    processed = fields.Integer(compute='_compute_statistics')
    rejected = fields.Integer(compute='_compute_statistics')
    total_sent = fields.Integer(compute='_compute_statistics')
    total_click = fields.Integer(compute='_compute_statistics')
    total_open = fields.Integer(compute='_compute_statistics')
    total_reply = fields.Integer(compute='_compute_statistics')
    total_bounce = fields.Integer(compute='_compute_statistics')
    total_delivered = fields.Integer(compute='_compute_statistics')

    received_ratio = fields.Integer(compute="_compute_statistics", string='Received Ratio')
    opened_ratio = fields.Integer(compute="_compute_statistics", string='Opened Ratio')
    replied_ratio = fields.Integer(compute="_compute_statistics", string='Replied Ratio')
    bounced_ratio = fields.Integer(compute="_compute_statistics", string='Bounced Ratio')

    @api.constrains('name', 'campaign_id')
    def _check_name_campaign(self):
        duplicates = self.search([('name', '=', self.name),('campaign_id', '=', self.campaign_id.id)])
        if duplicates.filtered(lambda a: a.id!=self.id):
            raise ValidationError(_("Activity Name must be unique per campaign"))


    @api.depends('interval_type', 'interval_number')
    def _compute_interval_standardized(self):
        factors = {'hours': 1,
                   'days': 24,
                   'weeks': 168,
                   'months': 720}
        for activity in self:
            activity.interval_standardized = activity.interval_number * factors[activity.interval_type]

    @api.depends('activity_type', 'trace_ids')
    def _compute_statistics(self):
        if not self.ids:
            self.update({
                'total_bounce': 0, 'total_reply': 0, 'total_sent': 0,
                'rejected': 0, 'total_click': 0, 'processed': 0, 'total_open': 0,
            })
        else:
            activity_data = {activity.id: {} for activity in self}
            for row in self._get_full_statistics():
                
                total = row['total'] or 1
                row['total_delivered'] = row['total_sent'] - row['total_bounce']
                row['received_ratio'] = 100.0 * row['total_delivered'] / total
                row['opened_ratio'] = 100.0 * row['total_open'] / total
                row['replied_ratio'] = 100.0 * row['total_reply'] / total
                row['bounced_ratio'] = 100.0 * row['total_bounce'] / total
                del row['total']
                activity_data[row.pop('activity_id')].update(row)

            
            for activity in self:
                activity.update(activity_data[activity.id])

    @api.multi
    def name_get(self):
        if 'parent_activity' in self._context.keys():
            activity_ids = []
            res = []
            id_current = False
            name_current = False
            if not isinstance(self._context.get('id_activity'), int) and 'one2many_v_id' in self._context.get('id_activity'):
                id_current = int(self._context.get('id_activity').split('_')[-1])
            if self._context.get('name_activity'):
                name_current = self._context.get('name_activity')
            for activity in self._context.get('parent_activity'):
                if activity and activity[0] in [4, 1] and isinstance(activity[1], int):
                    if not id_current or activity[1]!=id_current:
                        activity_ids.append(activity[1])
                elif activity and activity[0] == 0:
                    if not name_current or name_current!=activity[2]['name']:
                        res.append((activity[2]['name'], activity[2]['name']))
            for activity in  self.search([('id', 'in', activity_ids)]):
                res.append((activity.id, activity.name))
            return res
        return super(MarketingActivity, self).name_get()

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if any(not activity._check_recursion() for activity in self):
            raise ValidationError(_("Error! You can't create recursive hierarchy of Activity."))

    @api.constrains('trigger_type', 'parent_id')
    def _check_trigger_begin(self):
        if any(activity.trigger_type == 'begin' and activity.parent_id for activity in self):
            raise ValidationError(_("Error! You can't define a child activity with a trigger of type 'begin'."))

    @api.model
    def create(self, values):
        campaign_id = values.get('campaign_id')
        if not campaign_id:
            campaign_id = self.default_get(['campaign_id'])['campaign_id']
        values['require_sync'] = self.env['marketing.automation.campaign'].browse(campaign_id).state == 'running'
        return super(MarketingActivity, self).create(values)

    def write(self, values):
        if any(field in values.keys() for field in ('interval_number', 'interval_type')):
            values['require_sync'] = True
        return super(MarketingActivity, self).write(values)

    def _get_full_statistics(self):
        self.env.cr.execute("""
            SELECT
                trace.activity_id,
                COUNT(stat.id) AS total,
                COUNT(CASE WHEN stat.bounced IS NULL THEN 1 ELSE null END) AS total_sent,
                -- COUNT(CASE WHEN stat.clicked IS NOT NULL THEN 1 ELSE null END) AS total_click,
                COUNT(CASE WHEN stat.replied IS NOT NULL THEN 1 ELSE null END) AS total_reply,
                COUNT(CASE WHEN stat.opened IS NOT NULL THEN 1 ELSE null END) AS total_open,
                COUNT(CASE WHEN stat.bounced IS NOT NULL THEN 1 ELSE null END) AS total_bounce,
                COUNT(CASE WHEN trace.state = 'processed' THEN 1 ELSE null END) AS processed,
                COUNT(CASE WHEN trace.state = 'rejected' THEN 1 ELSE null END) AS rejected
            FROM
                marketing_trace AS trace
            JOIN
                mail_mail_statistics AS stat
                ON (stat.marketing_trace_id = trace.id)
            JOIN
                marketing_participant AS part
                ON (trace.participant_id = part.id)
            WHERE
                trace.activity_id IN %s
            GROUP BY
                trace.activity_id;
        """, (tuple(self.ids), ))
        return self.env.cr.dictfetchall()

    def execute(self, domain=None):
        trace_domain = [
            ('state', '=', 'scheduled'),
            ('activity_id', 'in', self.ids),
            ('participant_id.state', '=', 'running'),
        ]
        if domain:
            trace_domain += domain

        traces = self.env['marketing.trace'].search(trace_domain)
        
        trace_to_activities = dict()
        for trace in traces:
            if trace.activity_id not in trace_to_activities:
                trace_to_activities[trace.activity_id] = trace
            else:
                trace_to_activities[trace.activity_id] |= trace
        for activity, traces in trace_to_activities.items():
            activity.execute_on_traces(traces)

    def get_statistics_bounced(self):
        statistics_ids = [trace.mail_statistics_ids[0].id for trace in self.trace_ids if trace.mail_statistics_ids and trace.mail_statistics_ids[0].bounced]
        return {
                'name': _('Bounced Mail Statistics'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mail.mail.statistics',
                'type': 'ir.actions.act_window',
                'res_id': False,
                'context': self._context,
                'domain': [('id', 'in', statistics_ids)],
                'target': 'current'
            }

    def get_statistics_sent(self):
        statistics_ids = [trace.mail_statistics_ids[0].id for trace in self.trace_ids if trace.mail_statistics_ids]
        return {
                'name': _('Sent Mail Statistics'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mail.mail.statistics',
                'type': 'ir.actions.act_window',
                'res_id': False,
                'context': self._context,
                'domain': [('id', 'in', statistics_ids)],
                'target': 'current'
            }

    def get_statistics_received(self):
        statistics_ids = [trace.mail_statistics_ids[0].id for trace in self.trace_ids if trace.mail_statistics_ids and trace.mail_statistics_ids[0].state=='sent']
        return {
                'name': _('Received Mail Statistics'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mail.mail.statistics',
                'type': 'ir.actions.act_window',
                'res_id': False,
                'context': self._context,
                'domain': [('id', 'in', statistics_ids)],
                'target': 'current'
            }

    def get_statistics_replied(self):
        statistics_ids = [trace.mail_statistics_ids[0].id for trace in self.trace_ids if trace.mail_statistics_ids and trace.mail_statistics_ids[0].replied]
        return {
                'name': _('Replied Mail Statistics'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mail.mail.statistics',
                'type': 'ir.actions.act_window',
                'res_id': False,
                'context': self._context,
                'domain': [('id', 'in', statistics_ids)],
                'target': 'current'
            }


    def get_statistics_opened(self):
        statistics_ids = [trace.mail_statistics_ids[0].id for trace in self.trace_ids if trace.mail_statistics_ids and trace.mail_statistics_ids[0].opened]
        return {
                'name': _('Opened Mail Statistics'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mail.mail.statistics',
                'type': 'ir.actions.act_window',
                'res_id': False,
                'context': self._context,
                'domain': [('id', 'in', statistics_ids)],
                'target': 'current'
            }



    def execute_on_traces(self, traces):
        self.ensure_one()
        new_traces = self.env['marketing.trace']

        if self.validity_duration:
            duration = relativedelta(**{self.validity_duration_type: self.validity_duration_number})
            invalid_traces = traces.filtered(lambda trace: not trace.schedule_date or trace.schedule_date + duration < Datetime.now())
            invalid_traces.action_cancel()
            traces = traces - invalid_traces

        if self.domain:
            rec_domain = expression.AND([safe_eval(self.campaign_id.domain), safe_eval(self.domain)])
        else:
            rec_domain = safe_eval(self.campaign_id.domain)
        if rec_domain:
            rec_valid = self.env[self.model_name].search(rec_domain)
            rec_ids_domain = set(rec_valid.ids)

            traces_allowed = traces.filtered(lambda trace: trace.res_id in rec_ids_domain)
            traces_rejected = traces.filtered(lambda trace: trace.res_id not in rec_ids_domain) 
        else:
            traces_allowed = traces
            traces_rejected = self.env['marketing.trace']

        if traces_allowed:
            activity_method = getattr(self, '_execute_%s' % (self.activity_type))
            activity_method(traces_allowed)
            new_traces |= self._generate_children_traces(traces_allowed)
            traces.mapped('participant_id').check_completed()

        if traces_rejected:
            traces_rejected.write({
                'state': 'rejected',
                'state_msg': _('Rejected by activity filter or record deleted / archived')
            })

        return new_traces

    def _execute_action(self, traces):
        if not self.server_action_id:
            return False
        traces_ok = self.env['marketing.trace']
        for trace in traces:
            action = self.server_action_id.with_context(
                active_model=self.model_name,
                active_ids=[trace.res_id],
                active_id=trace.res_id
            )
            try:
                action.run()
            except Exception as e:
                _logger.warning(_('Marketing Automation: activity <%s> encountered server action issue %s'), self.id, str(e), exc_info=True)
                trace.write({
                    'state': 'error',
                    'schedule_date': Datetime.now(),
                    'state_msg': _('Exception in server action: %s') % e.message,
                })
            else:
                traces_ok |= trace
        traces_ok.write({
            'state': 'processed',
            'schedule_date': Datetime.now(),
        })
        return True

    def _execute_email(self, traces):
        res_ids = traces.mapped('res_id')
        
        mailing = self.mass_mailing_id.with_context(
            default_marketing_activity_id=self.ids[0],
            active_ids=res_ids
        )
        try:
            mailing.send_mail()
        except Exception as e:
            _logger.warning(_('Marketing Automation: activity <%s> encountered mass mailing issue %s'), self.id, str(e), exc_info=True)
            traces.write({
                'state': 'error',
                'schedule_date': Datetime.now(),
                'state_msg': _('Exception in mass mailing: %s') % e.message,
            })
        else:
            traces.write({
                'state': 'processed',
                'schedule_date': Datetime.now(),
            })
        return True

    def _generate_children_traces(self, traces):
        child_traces = self.env['marketing.trace']
        for activity in self.child_ids:
            activity_offset = relativedelta(**{activity.interval_type: activity.interval_number})

            for trace in traces:
                vals = {
                    'parent_id': trace.id,
                    'participant_id': trace.participant_id.id,
                    'activity_id': activity.id
                }
                if activity.trigger_type in ['act', 'mail_not_open', 'mail_not_click', 'mail_not_reply']:
                    vals['schedule_date'] = Datetime.from_string(trace.schedule_date) + activity_offset
                child_traces |= child_traces.create(vals)

        return child_traces
22