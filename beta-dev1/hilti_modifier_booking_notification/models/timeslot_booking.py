
from odoo import models, fields, api, _

class timeslot_booking(models.Model):
    
    _inherit = 'timeslot.booking'
    
    @api.model
    def create(self, vals):
        rec = super(timeslot_booking, self).create(vals)
        if 'is_reschedule' in self._context and self._context.get('is_reschedule'):
            rec.pr_booking_id.send_booking_reschedule_notification()
        return rec