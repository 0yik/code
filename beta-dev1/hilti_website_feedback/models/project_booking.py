# -*- coding: utf-8 -*-

from odoo import models, fields, api


class project_booking(models.Model):
    
    _inherit = 'project.booking'
    
    feedback_rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ])
    feedback_description = fields.Text()
    feedback_received = fields.Boolean()
    
    @api.model
    def booking_mobile_dashboard(self, days='all', completed_bookings_fields=[], fields=[]):
        completed_bookings_fields += ['feedback_description', 'feedback_received', 'feedback_rating']
        return super(project_booking, self).booking_mobile_dashboard(days=days, completed_bookings_fields=completed_bookings_fields, fields=fields)

    
    def send_booking_customer_feedback_notification(self):
        customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_customer_feedback_customer')
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_customer_feedback_tester')
        admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_customer_feedback_admin')
        notification_message = 'Customer gave the feedback for booking referenced as' + self.booking_no + '.'
        self.send_notification(customer_template, tester_template, admin_template, notification_message)
        return True
    
    def send_booking_complete_notification(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        customer_template = self.env.ref('hilti_website_feedback.mail_template_booking_feedback')
#         tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_complete_tester')
#         admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_booking_complete_admin')
        notification_message = 'Requested for feedback of customer for booking no' + self.booking_no + '.'
        if self.user_id and self.user_id.id:
            user_ids = [self.user_id.id]
        else:
            user_ids = []
        customer_template.with_context(feedback_url=base_url+'/booking_feedback?id=' + str(self.id)).send_mail(self.id, force_send=True)
        if self.tester_id:
            user_ids.append(self.user_tester_id.id)
#             tester_template.send_mail(self.id, force_send=True)
              
        admins = self.env.ref('hilti_modifier_accessrights.group_hilti_admin')
        for admin in admins.users:
            user_ids.append(admin.id)
#             admin_template.with_context(user_email=admin.partner_id.id).send_mail(self.id, force_send=True)
#              
        self.env['notification.notification'].create({
            'name': notification_message,
            'booking_id': self.id,
#             'ref_number': self.booking_no,
            'user_ids': [[6, 0, user_ids]]
        })
        return True
    
    @api.multi
    def write(self, vals):
        res = super(project_booking, self).write(vals)
        if vals.get('status') == 'completed':
            for rec in self:
                rec.send_booking_complete_notification()
        return res