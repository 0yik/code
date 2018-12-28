
from odoo import models, fields, api, _


class reschedule_booking(models.TransientModel):
    
    _inherit = 'reschedule.booking'
    
    @api.multi
    def reschedule_booking(self):
        res = super(reschedule_booking, self).reschedule_booking()
        self.env[self._context.get('active_model')].sudo().browse(self._context.get('active_id')).send_booking_reschedule_notification()
        return res