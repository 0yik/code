# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, tools, _

class calendar_event(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def default_get(self, fields):
        rec = super(calendar_event, self).default_get(fields)
        rec.update({
            'partner_ids': [(6, 0, [])],
        })
        return rec

    @api.model
    def create(self, vals):
        if self._context.get('active_model') == 'crm.lead':
            vals.update({'opportunity_id':self._context.get('active_id')})
            vals.update({'partner_ids':[(6,0, [self.env.user.partner_id.id])]})
        return super(calendar_event, self).create(vals)

# class crm_phonecall(models.Model):
#     _inherit = "crm.phonecall"

#     @api.model
#     def default_get(self, fields):
#         rec = super(crm_phonecall, self).default_get(fields)
#         rec.update({
#             'opportunity_id': self._context.get('opportunity_id'),
#         })
#         return rec

#     @api.model
#     def create(self, vals):
#         if self._context.get('active_model') == 'crm.lead':
#             vals.update({'opportunity_id':self._context.get('active_id')})
#         return super(crm_phonecall, self).create(vals)

class ActivityLog(models.TransientModel):

    _inherit = "crm.activity.log"

    partner_id = fields.Many2one('res.partner', string='Customer')
    phone = fields.Char('Phone')
    email_from = fields.Char('Email')
    street = fields.Char('Street')
    # street2 = fields.Char('Street2')
    # zip = fields.Char('Zip', change_default=True)
    # city = fields.Char('City')
    # state_id = fields.Many2one("res.country.state", string='State')
    # country_id = fields.Many2one('res.country', string='Country')
    # phonecall_ids = fields.One2many('crm.phonecall', 'opportunity_id',string='Logged Calls')
    meeting_ids = fields.One2many('calendar.event','opportunity_id',string='Meetings')

    @api.onchange('lead_id')
    def onchange_lead_id(self):
        # phonecall_obj = self.env['crm.phonecall'].search([('opportunity_id','=',self.lead_id.id)])
        # phonecall_list = []
        meeting_list = []
        # for p_id in phonecall_obj:
        #     phonecall_list.append(p_id.id)

        meeting_obj = self.env['calendar.event'].search([('opportunity_id','=',self.lead_id.id)])
        for m_id in meeting_obj:
            meeting_list.append(m_id.id)

        self.next_activity_id = self.lead_id.next_activity_id
        self.date_deadline = self.lead_id.date_deadline
        self.team_id = self.lead_id.team_id
        self.planned_revenue = self.lead_id.planned_revenue
        self.title_action = self.lead_id.title_action
        self.partner_id = self.lead_id.partner_id.id
        self.street = self.lead_id.street
        # self.street2 = self.lead_id.street2
        # self.city = self.lead_id.city
        # self.zip = self.lead_id.zip
        # self.state_id = self.lead_id.state_id.id
        # self.country_id = self.lead_id.country_id.id
        self.email_from = self.lead_id.email_from
        self.phone = self.lead_id.phone
        # if phonecall_list:
        #     self.phonecall_ids = [(6, 0, phonecall_list)]
        if meeting_list:
            self.meeting_ids = [(6, 0, meeting_list)]

    @api.multi
    def action_log(self):
        for log in self:
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
                'email_from':log.email_from,
                'phone':log.phone,
                'partner_id':log.partner_id.id,
                'street':log.street,
                # 'street2':log.street2,
                # 'city':log.city,
                # 'zip':log.zip,
                # 'state_id':log.state_id.id,
                # 'country_id':log.country_id.id,
            })
        return True