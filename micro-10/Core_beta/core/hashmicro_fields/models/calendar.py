from odoo import api, fields, models


class CalendarEvent(models.Model):

    _inherit = 'calendar.event'

    reseller_id = fields.Many2one('crm.reseller', 'Reseller', domain="[('type', '=', 'opportunity')]")
    summary_text = fields.Text('Summary Text')

    @api.model
    def create(self, vals):
        event = super(CalendarEvent, self).create(vals)
        if event.reseller_id:
            event.reseller_id.log_meeting(event.name, event.start, event.duration)
        return event
