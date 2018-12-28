# -*- coding: utf-8 -*-

from odoo import models,api,fields

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    @api.multi
    def _events_count(self):
        for serial_no in self:
            serial_no.events_count = 0 #len(serial_no.calendar_event_ids)
        

    events_count = fields.Integer(compute='_events_count', string='# Events')
    
    @api.multi
    def action_view_events(self):
        
        return
    