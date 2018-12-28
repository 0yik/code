from datetime import datetime, timedelta

from odoo import api, fields, models, tools, _

class CalenderEvent(models.Model):
     
    _inherit ="calendar.event"
     
    @api.model
    def create(self, vals):
        if self._context.get('active_model',False)=='crm.lead':
            vals['opportunity_id']=self._context.get('active_id')
        return super(CalenderEvent, self).create(vals)

class ActivityLog(models.TransientModel):

    _inherit = "crm.activity.log"

    def _default_stage_id(self):
        team = self.env['crm.team'].sudo()._get_default_team_id(user_id=self.env.uid)
        return self.env['crm.lead']._stage_find(team_id=team.id, domain=[('fold', '=', False)]).id

    name = fields.Char('Opportunity', required=False, index=True)
    partner_id = fields.Many2one('res.partner', string='Customer', track_visibility='onchange', index=True,
        help="Linked partner (optional). Usually created when converting the lead.")
    email_from = fields.Char('Email', help="Email address of the contact", index=True)
    stage_id = fields.Many2one('crm.stage', string='Stage', track_visibility='onchange', index=True,
        group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())
    date_action = fields.Date('Activity Date', index=True)
    phone = fields.Char('Phone')
#     priority = fields.Selection(crm_stage.AVAILABLE_PRIORITIES, string='Rating', index=True, default=crm_stage.AVAILABLE_PRIORITIES[0][0])
    meeting_ids = fields.One2many('calendar.event', 'opportunity_id',string='Meetings')

    @api.multi
    def action_log(self):
        for log in self:
            if self._context.get('active_id',False):
                opportinity = self.env['crm.lead'].browse(self._context['active_id'])
                values = {'name' : log.name,
                         'partner_id' : log.partner_id.id,
                         'email_from' : log.email_from,
                         'next_activity_id' : log.next_activity_id.id,
                         'title_action' : log.title_action,
                         'date_action' : log.date_action,
                         'planned_revenue' : log.planned_revenue,
                         'date_deadline' : log.date_deadline,
                         'description' : log.note
                        }
                opportinity.write(values)
            body_html = "<div><b>%(title)s</b>: %(next_activity)s</div>%(description)s%(note)s" % {
                'title': _('Activity Done'),
                'next_activity': log.next_activity_id.name,
                'description': log.title_action and '<p><em>%s</em></p>' % log.title_action or '',
                'note': log.note or '',
            }
            log.lead_id.message_post(body_html, subject=log.title_action, subtype_id=log.next_activity_id.subtype_id.id)
            log.lead_id.write({
                'date_deadline': log.date_deadline,
                'planned_revenue': log.planned_revenue,
                'title_action': False,
                'date_action': False,
                'next_activity_id': False,
            })
        return True

    @api.onchange('lead_id')
    def onchange_lead_id(self):
        res = super(ActivityLog, self).onchange_lead_id()
        self.name = self.lead_id.name
        self.phone = self.lead_id.phone
        self.date_action = self.lead_id.date_action
        self.stage_id = self.lead_id.stage_id
        self.email_from = self.lead_id.email_from
        self.partner_id = self.lead_id.partner_id
        self.note = self.lead_id.description
        return res
