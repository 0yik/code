# -*- coding: utf-8 -*-

from odoo import models,api,fields

class stock_production_lot(models.Model):
    _inherit='stock.production.lot'
    
    calendar_event_ids = fields.Many2many('calendar.event','stock_production_lot_calendar_event_rel','serial_id','event_id',"Events")
    
    @api.multi
    def _events_count(self):
        r = {}
        for serial_no in self:
            serial_no.events_count = len(serial_no.calendar_event_ids)
        return r

    events_count = fields.Integer(compute='_events_count', string='# Events')
    
    
    @api.multi
    def action_view_events(self):
        events = self.calendar_event_ids
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
        