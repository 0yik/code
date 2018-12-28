# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import datetime


class SendNotification(models.Model):
    _name = 'send.notification.app'
    _description = 'Send Notification to App'

    @api.model
    def send_update_to_app(self):
        print 'FFFFFFFFFFF'
        wo_pool = self.env['stock.picking']
        date_today = fields.Datetime.from_string(fields.Datetime.now())
        print "DDDDDDDDDD", date_today
        from_date = (date_today + datetime.timedelta(days=1)).replace(
            hour=00, minute=00, second=01)
        to_date = (date_today + datetime.timedelta(days=1)).replace(
            hour=23, minute=59, second=59)
        print "UPdated date", from_date,  to_date
        wo_ids = wo_pool.search(
            [('scheduled_start', '>=', fields.Datetime.to_string(from_date)),
             ('scheduled_start', '<=', fields.Datetime.to_string(to_date)),
             ])
        print "$$$$$$$$VVVVVVVVVVV", wo_ids
        if not wo_ids:
            return False
        return True


SendNotification()
