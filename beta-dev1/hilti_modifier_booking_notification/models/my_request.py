
from odoo import models, fields, api, _

class tester_myreqest(models.Model):
    
    _inherit = 'my.request'
    
    @api.model
    def create(self, vals):
        res = super(tester_myreqest, self).create(vals)
        user_ids = []
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_tester_request_tester')
        admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_tester_request_admin')
        notification_message = 'A request has been received which is referenced as ' + res.req_no + '.'
        if res.user_id:
            user_ids.append(res.user_id.id)
            tester_template.send_mail(res.id, force_send=True)
        admins = self.env.ref('hilti_modifier_accessrights.group_hilti_admin')
        for admin in admins.users:
            user_ids.append(admin.id)
            admin_template.with_context(user_email=admin.partner_id.id).send_mail(res.id, force_send=True)
        self.env['notification.notification'].create({
            'name': notification_message,
            'tester_request_id': res.id,
#             'ref_number': res.req_no,
            'user_ids': [[6, 0, user_ids]]
        })
        return res
    
    @api.multi
    def write(self, vals):
        res = super(tester_myreqest, self).write(vals)
#         if 'status' and vals.get('status') == 'approved':
#             for rec in self:
#                 if (vals.get('req_type') == 'unavailability' or rec.req_type == "unavailability"):
#                     tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_tester_request_unavailability_approved_tester')
#                     notification_message = 'A request has been approved which is referenced as ' + rec.req_no + '.'
#                     user_ids = []
#                     if rec.user_id:
#                         user_ids.append(rec.user_id.id)
#                         tester_template.send_mail(rec.id, force_send=True)
#                     self.env['notification.notification'].create({
#                         'name': notification_message,
#                         'tester_request_id': rec.id,
#                         'user_ids': [[6, 0, user_ids]]
#                     })
        return res
    
    def _send_notification_force_approve(self, req_obj, booking_ids):
        res = super(tester_myreqest, self)._send_notification_force_approve(req_obj, booking_ids)
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_tester_request_unavailability_approved_tester')
        if req_obj.user_id:
            tester_template.send_mail(req_obj.id, force_send=True)
        self.env['notification.notification'].create({
            'name': 'A request has been Approved which is referenced as ' + req_obj.req_no + '.',
            'tester_request_id': req_obj.id,
            'user_ids': [[6, 0, [req_obj.user_id.id]]]
        })
        customer_template = self.env.ref('hilti_modifier_booking_notification.mail_template_tester_request_unavailability_approved_customer')
        for booking_rec in booking_ids:
            user_ids = []
            if booking_rec.user_id.id:
                user_ids.append(booking_rec.user_id.id)
                customer_template.send_mail(booking_rec.id, force_send=True)
            self.env['notification.notification'].create({
                'name': 'A tester who was assigned to your booking is not available on the booking date. So would you please reshcedule the booking referenced as ' + booking_rec.booking_no + '.',
                'booking_id': booking_rec.id,
                'user_ids': [[6, 0, user_ids]]
            })
        return res
    
    def send_notification_cancel(self, req_obj):
        res = super(tester_myreqest, self).send_notification_cancel(req_obj)
        user_ids = []
        tester_template = self.env.ref('hilti_modifier_booking_notification.mail_template_tester_request_cancel_tester')
        admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_tester_request_cancel_admin')
        notification_message = 'A request has been cancelled which is referenced as ' + req_obj.req_no + '.'
        if req_obj.user_id:
            user_ids.append(req_obj.user_id.id)
            tester_template.send_mail(req_obj.id, force_send=True)
        admins = self.env.ref('hilti_modifier_accessrights.group_hilti_admin')
        for admin in admins.users:
            user_ids.append(admin.id)
            admin_template.with_context(user_email=admin.partner_id.id).send_mail(req_obj.id, force_send=True)
        self.env['notification.notification'].create({
            'name': notification_message,
            'tester_request_id': req_obj.id,
            'user_ids': [[6, 0, user_ids]]
        })
        return res
    
