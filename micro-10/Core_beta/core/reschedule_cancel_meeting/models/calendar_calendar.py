from odoo import models, api, fields

class calendar_event(models.Model):
    _inherit = 'calendar.event'

    reason_id = fields.Many2one('calendar.reasons',string="Reason")
    reason_description = fields.Text(string="Reason Description")
    state = fields.Selection([('schedule','Schedule'),('cancel','Cancel')], string="State", default="schedule")
