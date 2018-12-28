# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import ValidationError, Warning as UserError
import logging
logger = logging.getLogger(__name__)

class SubstituteWizard(models.TransientModel):
    _name = 'substitute.wizard'
    
    teacher_id = fields.Many2one('hr.employee','Teacher',required=True)
    subject_ids = fields.Many2many('subject.subject','subject_substitute_rel','substitute_wizard_id','subject_id','Subjects',readonly=False)
    
    @api.multi
    def add_substitute_teacher(self):
        attendance_pool = self.env['daily.attendance']
        total_class = ''
        temp = 0
        for active_id in self._context.get('active_ids'):
            attendance_obj = attendance_pool.browse(active_id)
            if attendance_obj.state == 'draft':
                start_time = attendance_obj.class_id.start_time
                end_time = attendance_obj.class_id.end_time
                attendance_ids = attendance_pool.search([
                    ('date','>',start_time),
                    #('end_time','<',end_time),
                    ('date','<',end_time),
                    ('teacher_id','=',self.teacher_id.id)
                ])
                attendance_name = ''
                if attendance_ids:
                    for attendance_id in attendance_ids:
                        attendance_name += attendance_id.class_id.name + ' | '
                    raise UserError(_('%s is already assigned in attendance of %s for the same period !') % (self.teacher_id.name, attendance_name[:-3]))
                else:
                    if not attendance_obj.is_substitute:
                	    attendance_obj.write({'subtitute_teacher_id': attendance_obj.teacher_id and attendance_obj.teacher_id.id or False})
                	    attendance_obj.class_id.write({'subtitute_teacher_id': attendance_obj.teacher_id and attendance_obj.teacher_id.id or False})
                    attendance_obj.class_id.write({
                    	'teacher_id': self.teacher_id and self.teacher_id.id or False,
                    	'assign_sustitute_date': fields.Date.today(),
                    	'is_substitute': True
                	})
                    attendance_obj.write({
                    	'teacher_id': self.teacher_id and self.teacher_id.id or False,
                    	'assign_sustitute_date': fields.Date.today(),
                    	'is_substitute': True
                	})
                    temp = 1
                    total_class += attendance_obj.class_id.name +'<br/>'
        # Substitute Teacher Email Notification
        if temp == 1:
            admin = self.env['res.users'].browse(self._uid)
            recipient_ids = [self.teacher_id.id]
            substitute_msg = self.env.ref('assign_substitute_teacher.substitute_teacher_email_verification').value
            mail_body = '<b>' + self.teacher_id.name +'</b>,<br/><br/>', '<br/><b>'+ total_class +'</b><br/><br/>'
            mail_vals = {
                'subject':'Substitute Teacher Email Notification',
                'author_id':self.env.user.partner_id.id,
                'email_from':admin.partner_id.email or '',
                'email_to':self.teacher_id.work_email,
                'reply_to':admin.partner_id.email,
                'body_html':str(substitute_msg)%(mail_body),
            }
            mail_sent = self.env['mail.mail'].create(mail_vals).send()
        # END Substitute Teacher Email Notification
        return True

