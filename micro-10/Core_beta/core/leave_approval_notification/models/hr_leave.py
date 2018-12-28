# -*- coding: utf-8 -*-
import time
from datetime import date, datetime
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT



class Holidays(models.Model):
    _inherit = 'hr.holidays'
    
    @api.multi
    def action_approve(self):
        rec = super(Holidays, self).action_approve()
        school_admin_group_id = self.env.ref('school.group_school_administration')
        approval_msg = self.env.ref('leave_approval_notification.leave_approval_email_verification').value
        admin = self.env['res.users'].browse(self._uid)
        if school_admin_group_id and school_admin_group_id.users:
            for user in school_admin_group_id.users:
                if self.type == 'remove':
                    mail_body = '<b>' + user.partner_id.name +'</b>,<br/>','<b>'+self.employee_id.name+'</b>','<b>'+self.date_from+'</b>','<b>'+self.date_to+'</b>','<b>'+str(self.number_of_days_temp)+'</b>' +' days.<br/>'
                    mail_vals = {
                        'subject':'Leave Approval Notification for teacher %s'%(self.employee_id.name),
                        'author_id':self.env.user.partner_id.id,
                        'email_from':admin.partner_id.email or '',
                        'recipient_ids':[(4,[user.partner_id.id])],
                        'reply_to':admin.partner_id.email,
                        'body_html':str(approval_msg)%(mail_body),
                    }
                    mail_sent = self.env['mail.mail'].create(mail_vals).send()
        return rec


class HrLeaveConfigSettings(models.TransientModel):
    _inherit = 'hr.leave.config.settings'

    
    leave_approval_email = fields.Html('Leave Approval Email Notification to Admin Group', help='Leave Approval Email Notification to Admin Group')
    
    
    @api.model
    def get_default_leave_approval_email(self, fields):
        leave_approval_email = self.env.ref('leave_approval_notification.leave_approval_email_verification').value
        return {'leave_approval_email': leave_approval_email}

    @api.multi
    def set_default_leave_approval_email(self):
        for record in self:
            self.env.ref('leave_approval_notification.leave_approval_email_verification').write({'value': record.leave_approval_email})

