# -*- coding: utf-8 -*-

from odoo import models, fields

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    work_order_id = fields.Many2one('stock.picking', string='Work Order')
    booking_order_id = fields.Many2one('sale.order', string='Booking Order')
    booking_order_status = fields.Selection(related="booking_order_id.state_booking",string="Status")

CalendarEvent()