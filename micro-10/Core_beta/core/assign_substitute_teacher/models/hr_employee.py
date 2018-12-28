# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime
from datetime import timedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(HrEmployee, self).name_search(name, args, operator, limit)
        new_res = []
        subject_pool = self.env['subject.subject']
        if self._context.has_key('for_substitute') and self._context.has_key('subject_ids'):
            if self._context.get('for_substitute') == True:
                subject_ids = self._context.get('subject_ids')[0][2]
                for subject_id in subject_ids:
                    subject_obj = subject_pool.browse(subject_id)
                    if subject_obj.teacher_ids:
                        for teacher in subject_obj.teacher_ids:
                            teacher_touple = (teacher.id, teacher.name)
                            new_res.append(teacher_touple)
                final_res = list(set(new_res))
                return final_res
        else:
            return res
            
class DailyAttendance(models.Model):
    _inherit = 'daily.attendance'
    
    @api.multi
    def cron_admin_substitute_notification(self):
        attendance_pool = invoice_pool = self.env['daily.attendance']
        attendance_ids = invoice_pool.search([('state','=', 'draft'),('is_substitute','=', True)])
        admin_notification = int(self.env.ref('assign_substitute_teacher.admin_notification_day').value)
        admin = self.env['res.users'].sudo().browse(self._uid)
        for attendance_id in attendance_ids:
            if attendance_id.assign_sustitute_date:
                sustitute_date = datetime.strptime(str(attendance_id.assign_sustitute_date),"%Y-%m-%d")
                today = datetime.strptime(str(datetime.today().strftime('%Y-%m-%d')),"%Y-%m-%d")
                difference_date = (today - sustitute_date).days
                body = 'Hi <b>'+ admin.name +'</b>,\n\n' +'Please check whether <b>'+ attendance_id.teacher_id.name +'</b> has confirmed for the <b>' +attendance_id.class_id.name+ '</b> on email.'
                if difference_date >= admin_notification:
                    mail_vals = {
                        'subject':'Check Confirmation of Substitute Teacher.',
                        'author_id':admin.id,
                        'email_from':admin.partner_id.email or '',
                        'recipient_ids':[(4,[admin.partner_id.id])],
                        'reply_to':admin.partner_id.email,
                        'body_html':str(body),
                    }
                    mail_sent = self.env['mail.mail'].create(mail_vals).send()
        return True
    
    assign_sustitute_date = fields.Date('Substitute Date')
    subtitute_teacher_id = fields.Many2one('hr.employee','Original Teacher',domain="[('is_school_teacher','=', True)]")
    is_substitute = fields.Boolean('Substitute Class')
            
class EmsClass(models.Model):
    _inherit = 'ems.class'
    
    assign_sustitute_date = fields.Date('Substitute Date')
    subtitute_teacher_id = fields.Many2one('hr.employee','Original Teacher',domain="[('is_school_teacher','=', True)]")
    is_substitute = fields.Boolean('Substitute Class')


class HrLeaveConfigSettings(models.TransientModel):
    _inherit = 'hr.leave.config.settings'

    
    substitute_teacher_email = fields.Html('Substitute Teacher Email Notification', help='Substitute Teacher Email Notification')
    admin_notification = fields.Char('Notification Days', help='Substitute Teacher Email Notification to Admin after given day.')
    
    
    @api.model
    def get_default_substitute_teacher_email(self, fields):
        substitute_teacher_email = self.env.ref('assign_substitute_teacher.substitute_teacher_email_verification').value
        return {'substitute_teacher_email': substitute_teacher_email}

    @api.multi
    def set_default_substitute_teacher_email(self):
        for record in self:
            self.env.ref('assign_substitute_teacher.substitute_teacher_email_verification').write({'value': record.substitute_teacher_email})
            
    @api.model
    def get_default_admin_notification(self, fields):
        admin_notification = self.env.ref('assign_substitute_teacher.admin_notification_day').value
        return {'admin_notification': admin_notification}

    @api.multi
    def set_default_admin_notification(self):
        for record in self:
            self.env.ref('assign_substitute_teacher.admin_notification_day').write({'value': record.admin_notification})

