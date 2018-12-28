# -*- coding: utf-8 -*-

from odoo import models,fields

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'
    
    serial_ids = fields.Many2many("stock.production.lot","serial_number_calendar_event_rel","event_id","serial_id","Equipments")
    employee_ids = fields.Many2many("hr.employee","employee_calendar_event_rel","event_id","employee_id","Employees")
    