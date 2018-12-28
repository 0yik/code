
from odoo import fields, models, api
from datetime import datetime

class CrmLead(models.Model):

    _inherit = 'crm.lead'

    meeting_ids = fields.One2many('calendar.event', 'opportunity_id',string='Meetings')
    
    @api.multi
    def action_schedule_meeting(self):
        """ Open meeting's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view
        """
        res = super(CrmLead, self).action_schedule_meeting()
        res['context']['default_location'] = self.street
        res['context']['default_email'] = self.email_from
        res['context']['default_phone'] = self.phone
        res['context']['default_partner_ids'] = [(6,0,[self.user_id.partner_id.id])]
        if self.user_id2:
            res['context']['default_partner_ids'] = [(6,0,[self.user_id.partner_id.id])]
        return res

    @api.model
    def create(self, vals):
        res = super(CrmLead, self).create(vals)
        activity = res.next_activity_id
        if activity and activity.name.lower() == 'call':
            self.env['crm.phonecall'].create({'name':res.name,
                                              'date':res.date_action,
                                              'partner_id':res.partner_id.id,
                                              'partner_mobile':res.mobile,
                                              'partner_phone':res.phone,
                                              'opportunity_id':res.id,
                                              'user_id':res.user_id.id,
                                              'team_id':res.team_id.id,
                                            })
        return res

    @api.multi
    def write(self, vals):
        if vals.get('date_action', False) and vals.get('next_activity_id',False):
            activity = self.env['crm.activity'].browse(vals['next_activity_id'])
            if activity.name.lower() == 'call':
                self.env['crm.phonecall'].create({'name':self.name,
                                                  'date':vals['date_action'],
                                                  'partner_id':self.partner_id.id,
                                                  'partner_mobile':self.mobile,
                                                  'partner_phone':self.phone,
                                                  'opportunity_id':self.id,
                                                  'user_id':self.env.uid,
                                                  'team_id':self.team_id.id,
                                                })
        return super(CrmLead, self).write(vals)

class CrmActivity(models.Model):
    _inherit = 'crm.activity'
    
    @api.onchange('name')
    def onchange_name(self):
        self.description = self.name
    
class CrmPhonecall(models.Model):
    """ Model for CRM phonecalls """
    _inherit = "crm.phonecall"

    @api.onchange('opportunity_id')
    def on_change_opportunity(self):
        res = super(CrmPhonecall, self).on_change_opportunity()
        if self.opportunity_id:
            self.partner_mobile = self.opportunity_id.phone
        return res
