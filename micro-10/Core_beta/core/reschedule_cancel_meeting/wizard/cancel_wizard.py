from odoo import models, api, fields

class cancel_wizard(models.TransientModel):

    _name = 'cancel.wizard'
    
    reason_id = fields.Many2one('calendar.reasons',string="Reason", domain=[('reason_type', '=', 'reschedule_meeting')])
    remarks = fields.Text(string="Remarks")

    @api.multi
    def cancel_meeting(self):
        calendar = self.env['calendar.event'].sudo().browse(self._context.get('active_ids'))
        calendar.write({
            'state': 'cancel',
            'reason_id': self.reason_id.id, 
            'reason_description': self.remarks
        })
        if calendar.attendee_ids:
            calendar.attendee_ids.do_decline()
        return True
