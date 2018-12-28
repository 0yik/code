# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class product_inherit(models.Model):
    _inherit = 'product.template'

    is_equipment = fields.Boolean('Is an equipment')
    # serial_number = fields.One2many('stock.production.lot', )


class calendar_inherit(models.Model):
    _inherit = 'calendar.event'

    serial_numbers_ids = fields.Many2many('stock.production.lot')


class employee_inherit(models.Model):
    _inherit = 'hr.employee'

    def search_events(self):
        for record in self:
            partner = record.user_id.partner_id
            event_ids = []
            if partner and partner.id:
                events = self.env['calendar.attendee'].search([('partner_id', '=', partner.id)])
                for event in events:
                    event_ids.append(event.event_id.id)
            if len(event_ids) > 0:
                return {
                    'name': 'Events',
                    'type': 'ir.actions.act_window',
                    'view_type': 'calendar',
                    'view_mode': 'calendar,tree,form',
                    'res_model': 'calendar.event',
                    'domain': [('id', 'in', event_ids)],
                    'target': 'current',
                }
            else:
                return {
                    'name': 'Events',
                    'type': 'ir.actions.act_window',
                    'view_type': 'calendar',
                    'view_mode': 'calendar,tree,form',
                    'res_model': 'calendar.event',
                    'target': 'current',
                }


class stock_production_lot_inherit(models.Model):
    _inherit = 'stock.production.lot'

    calendar_event_ids = fields.Many2many('calendar.event')

    def search_lot_number(self):
        for record in self:
            list_calender_event = []
            events = record.calendar_event_ids
            for event in events:
                list_calender_event.append(event.id)

            return {
                'name': 'Events',
                'type': 'ir.actions.act_window',
                'view_type': 'calendar',
                'view_mode': 'calendar,tree,form',
                'res_model': 'calendar.event',
                'domain': [('id', 'in', list_calender_event)],
                'target': 'current',
            }
