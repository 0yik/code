from odoo import models, api, fields

class calendar_reasons(models.Model):
    _name = 'calendar.reasons'
    
    name = fields.Text(string="Reason")
    reason_type = fields.Selection([('reschedule_meeting','Reschedule Meeting'),('cancel_meeting','Cancel Meeting')], string="Reason Type")
    active = fields.Boolean(string="Active", default=True)