from odoo import models, fields

class resource_calendar(models.Model):
    _inherit = 'resource.calendar'

    schedule = fields.Selection([('fixed_schedule', 'Fixed Schedule'),
                                 ('flexible_schedule', 'Flexible Schedule'),
                                 ], string='Schedule', default='fixed_schedule')

resource_calendar()

class resource_calendar_attendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    alternate_week = fields.Boolean('Alternate Week')
    schedule = fields.Selection(related="calendar_id.schedule", string='Schedule', store=True)
    working_hours = fields.Float('Working Hours')

resource_calendar_attendance()