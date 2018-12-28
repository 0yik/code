# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Wizard(models.TransientModel):
    _inherit = 'booking.order.wizard'

    noti = fields.Char()

    @api.multi
    def action_confirm(self):
        context = self.env.context
        if context.get('active_id', False) and context.get('active_model', False) == 'sale.order':
            booking = self.env['sale.order'].browse(context.get('active_id'))
            booking.action_confirm_record()
            booking.action_create_calendar()
        return True

Wizard()