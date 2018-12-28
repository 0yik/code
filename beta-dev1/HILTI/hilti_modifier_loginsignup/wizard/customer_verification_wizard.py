# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class customer_verification_wizard(models.TransientModel):
    
    _name = 'customer.verification.wizard'
    
    def _default_user_ids(self):
        return self._context.get('active_ids') or []
    
    user_ids = fields.Many2many('res.users', string='Users', default=_default_user_ids)
    
    @api.multi
    def verify_button(self):
        if self._context.get('approve'):
            self.env['res.users'].browse(self._context.get('active_ids')).write({
                'active': True
            })
        else:
            self.env['res.users'].browse(self._context.get('active_ids')).write({
                'active': False
            })
        return True