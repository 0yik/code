# -*- coding: utf-8 -*-

from odoo import models,api,fields

class SerialNumbers(models.Model):
    _inherit='stock.production.lot'
    
    @api.multi
    def _total_events(self):
        for record in self:
            record.events_count = len(record.event_ids)    

    event_ids = fields.Many2many("calendar.event","serial_number_calendar_event_rel","serial_id","event_id","Events")
    events_count = fields.Integer(compute="_total_events", string="Events")
    
    
    @api.multi
    def action_view_events(self):
        events = self.event_ids
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        if len(events) > 1:
            action['domain'] = [('id', 'in', events.ids)]
            action['views'] = [(self.env.ref('calendar.view_calendar_event_tree').id, 'tree')]
        elif len(events) == 1:
            action['views'] = [(self.env.ref('calendar.view_calendar_event_form').id, 'form')]
            action['res_id'] = events.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
        