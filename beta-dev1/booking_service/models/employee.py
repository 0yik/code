# -*- coding: utf-8 -*-

from odoo import models,api,fields

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    @api.multi
    def _total_events(self):
        calendar_event = self.env['calendar.event']
        event_ids = []
        for emp in self:
            event_ids = calendar_event.search([('employee_ids','in',[emp.id])])
        self.total_events = len(event_ids)
            
    total_events = fields.Integer(compute='_total_events', string='Events')
    
    @api.multi
    def employee_events(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        if action:
            action['domain'] = [('employee_ids','in',self.id)]
        return action