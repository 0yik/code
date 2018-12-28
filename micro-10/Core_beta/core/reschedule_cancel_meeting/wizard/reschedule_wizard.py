from odoo import models, api, fields
from datetime import datetime, timedelta

class reschedule_wizard(models.TransientModel):
    _name = 'reschedule.wizard'

    @api.model
    def _default_start_datetime(self):
        if self._context.get('active_id'):
            return self.env['calendar.event'].browse(self._context.get('active_id')).start_datetime
    
    @api.model
    def _default_duration(self):
        if self._context.get('active_id'):
            return self.env['calendar.event'].browse(self._context.get('active_id')).duration
    
    @api.model
    def _default_allday(self):
        if self._context.get('active_id'):
            return self.env['calendar.event'].browse(self._context.get('active_id')).allday

    reason_id = fields.Many2one('calendar.reasons',string="Reason", domain=[('reason_type', '=', 'reschedule_meeting')])
    start_datetime = fields.Datetime(string="Starting at", default=_default_start_datetime)
    duration = fields.Float(string="Duration", default=_default_duration)
    allday = fields.Boolean(string="Allday", default=_default_allday)

    def reschedule_meeting(self):
        calendar = self.env['calendar.event'].sudo().browse(self._context.get('active_ids'))
        vals = {
            'start_datetime': self.start_datetime,
            'duration': self.duration,
            'start': self.start_datetime,
            'stop': fields.Datetime.to_string(fields.Datetime.from_string(self.start_datetime) + timedelta(hours=self.duration)),
            'reason_id': self.reason_id.id,
            'allday': self.allday,
        }
        return calendar.write(vals)