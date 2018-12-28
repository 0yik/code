from odoo import fields, models, api
from datetime import datetime

class CalendarEvent(models.Model):
    
    _inherit = "calendar.event"

    email = fields.Char('Email')
    phone = fields.Char('Phone')