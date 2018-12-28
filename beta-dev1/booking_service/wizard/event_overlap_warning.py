# -*- coding: utf-8 -*-

from odoo import api, fields, models

class EquipmentsOverlapWarnings(models.TransientModel):
    _name = "event.overlap.warning"

    name = fields.Char("Warning message")
    
    @api.model
    def default_get(self, fields):
        result = super(EquipmentsOverlapWarnings, self).default_get(fields)
        if self._context.get('warning_message',''):
            result['name'] = self._context.get('warning_message','')
        return result    
        
    @api.multi
    def action_confirm(self):
        active_id = self._context.get("active_id")
        if active_id:
            ctx = self._context.copy()
            ctx.update({'process_event_booking': True})
            self.env['sale.order'].browse(active_id).with_context(ctx).action_confirm()
        return True
