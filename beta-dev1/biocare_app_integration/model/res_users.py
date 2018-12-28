# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    show_notification = fields.Boolean('Show Notification',default=True)
    notification_date = fields.Datetime('Notification')

    @api.multi
    def toggle_show_notification(self):
        for record in self:
            record.show_notification = not record.show_notification

    @api.multi
    def update_user_notification(self, notification):
        user_obj = self.env.user
        if notification:
            user_obj.show_notification = True
            user_obj.notification_date = ''
            return True
        else:
            user_obj.show_notification = False
            user_obj.notification_date = fields.Datetime.now()
            return False

ResUsers()