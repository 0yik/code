# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Wizard(models.TransientModel):
    _name = 'work.order.wizard'

    work_employees = fields.Many2many('hr.employee', string='Employees')
    noti = fields.Char()

    @api.multi
    def action_confirm(self):
        context = self.env.context
        if context.get('active_id', False) and context.get('active_model', False) == 'stock.picking':
            picking = self.env['stock.picking'].browse(context.get('active_id'))
            picking.action_create_calendar()
            picking.action_confirm()
            picking.is_validated = True
            picking.state = 'pending'
        return True