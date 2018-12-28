
from odoo import fields, api, models
from odoo.exceptions import Warning

class CRMTeam(models.Model):
    _inherit = 'crm.team'
    
    def _get_current_user(self):
        userlist= []
        return [('id', '=', self.env.uid)]

    achievement_member_ids = fields.One2many('res.users', 'sale_team_id',domain=_get_current_user, string='Team Members')
    
    @api.multi
    def open_popup_id(self):        
        context = dict(self.env.context or {})
        if not context.has_key('active_id'):
            context['active_id'] = self.id
            return {
                'name': 'Sales Target & Achievement',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'crm.team',
                'view_id': self.env.ref('salestarget_achievement_popup_window__ipt_custom.crm_team_popup_view_form').id,
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'context': context,
                'target': 'new',
            }

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @api.multi
    def get_phonecall_ids(self):
        for rc in self:
            result_ids = self.env['crm.phonecall'].search([('user_id','=',rc.id)])
            rc.phonelog_ids = self.env['crm.phonecall'].browse([x.id for x in result_ids])
            
    @api.multi
    def get_emails_ids(self):
        for rc in self:
            self.env.cr.execute(''' select mail_mail_id from mail_mail_res_partner_rel where res_partner_id = %s; '''%rc.partner_id.id)
            kq = self.env.cr.dictfetchall()
            kq = list(set([x['mail_mail_id'] for x in kq]))
            if kq:
                rc.email_log_ids = self.env['mail.mail'].browse(kq)
                
    @api.multi
    def get_meeting_ids(self):
        for rc in self:
            self.env.cr.execute(''' select calendar_event_id from calendar_event_res_partner_rel where res_partner_id = %s; '''%rc.partner_id.id)
            kq = self.env.cr.dictfetchall()
            kq = list(set([x['calendar_event_id'] for x in kq]))
            if kq:
                rc.meeting_log_ids = self.env['calendar.event'].browse(kq)
    
    phonelog_ids = fields.Many2many('crm.phonecall', 'user_phonecall_rel', 'user_id', 'phonecall_id', compute='get_phonecall_ids', string='Phone Log')
    email_log_ids = fields.Many2many('mail.mail', 'user_email_rel', 'user_id', 'email_id', string='Email Log', compute='get_emails_ids')
    meeting_log_ids = fields.Many2many('calendar.event', 'user_meeting_rel', 'user_id', 'meeting_id', string='Meeting Log', compute='get_meeting_ids')
    