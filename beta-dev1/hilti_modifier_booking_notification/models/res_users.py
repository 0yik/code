
from odoo import models, fields, api, _

class res_users(models.Model):
    
    _inherit = 'res.users'
    
    @api.model
    def create(self, vals):
        res = super(res_users, self).create(vals)
        customer_group = self.env.ref('hilti_modifier_accessrights.group_hilti_customer')
        if self.has_group('hilti_modifier_accessrights.group_hilti_customer'):
            user_ids = []
            admin_template = self.env.ref('hilti_modifier_booking_notification.mail_template_new_user_registration_admin')
            notification_message = 'New customer has arrived whose name is ' + res.name + '.'
            admins = self.env.ref('hilti_modifier_accessrights.group_hilti_admin')
            for admin in admins.users:
                user_ids.append(admin.id)
                admin_template.with_context(user_email=admin.partner_id.id).send_mail(res.id, force_send=True)
            self.env['notification.notification'].create({
                'name': notification_message,
                'user_id': res.id,
                'user_ids': [[6, 0, user_ids]]
            })
        return res