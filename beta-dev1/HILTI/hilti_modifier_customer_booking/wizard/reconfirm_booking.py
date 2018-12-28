# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class reconfirm_booking(models.TransientModel):
    
    _name = 'reconfirm.booking'
    
    description = fields.Text(default='You want to re-confirm?')
    
    @api.multi
    def booking_reconfirm(self):
        self.env[self._context.get('active_model')].sudo().browse(self._context.get('active_id')).write({'status': 'reconfirmed'})
        return True
    
