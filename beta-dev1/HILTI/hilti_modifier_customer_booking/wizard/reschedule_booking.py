# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class reschedule_booking(models.TransientModel):
    
    _name = 'reschedule.booking'
    
    start_datetime = fields.Datetime("Start Time")
    end_datetime = fields.Datetime("End Time")
    
    @api.multi
    def reschedule_booking(self):
        vals = {}
        if self.start_datetime:
            vals.update({
                'start_date_time': self.start_datetime,
            })
        if self.end_datetime:
            vals.update({
                'end_date_time': self.end_datetime,
            })
        self.env[self._context.get('active_model')].sudo().browse(self._context.get('active_id')).write(vals)
        return True
    