from odoo import models, fields, api,_
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import pytz

class hr_employee(models.Model):
    _inherit = "hr.employee"

    events_ids = fields.One2many('calendar.event','employee_id')


    @api.multi
    def has_event(self):
        if not self:
            return

        datetime_now = datetime.utcnow()


        for event in self.events_ids:
            event = self.env['calendar.event'].with_context(tz='UTC').browse(event.id)
            event_start_time = event.start_datetime and datetime.strptime(event.start_datetime, '%Y-%m-%d %H:%M:%S')
            
            if event_start_time:
                event_end_time = event_start_time + timedelta(hours=event.duration)
            
                time_record =  self.env['booking.order.settings'].search([],limit=1)

                effective_start_time = event_start_time - timedelta(minutes=time_record.pre_booking)
                effective_end_time = event_end_time + timedelta(hours=time_record.post_booking)
            
                if datetime_now >= effective_start_time and datetime_now <= effective_end_time:

                    return True
        return False

    @api.multi
    def view_event(self):
        context = self._context.copy()
        return {
            'name':_('View Event'),
            'view_type':'form',
            'view_mode':'tree',
            'res_model': 'calendar.event',
            'view_id':self.env.ref('calendar.view_calendar_event_tree').id,
            'type': 'ir.actions.act_window',
            'domain':[('id','in',self.events_ids.ids)],
            'context':context,
            }