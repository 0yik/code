# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class admin_configuration(models.TransientModel):

    _name = 'admin.configuration'
    _inherit = 'res.config.settings'

    total_reminder = fields.Integer('Total Reminder')
    reminder_duration = fields.Integer('Reminder Duration')
    delay_time = fields.Integer('Delay Time')
    customer_booking_days = fields.Integer('Penalty days')
    ot_start_time = fields.Float('OT Start Time')
    ot_end_time = fields.Float('OT End Time')
    send_notification_on_cancel = fields.Boolean('Send mail on cancellation')
    reminder_sent_before_hours = fields.Integer('Time before when reminder notification is sent')
    action_needed_before_hours = fields.Integer('Time before action required for re-confirmation of booking')
    booking_before_time = fields.Float('Pre-Booking')
    booking_after_time = fields.Float('Post-Booking')
    calendar_display = fields.Integer('Display Calendar Months')
    hours_before_send_notification_for_dedicated_bookings = fields.Integer('Hours before send notification of for Dedicated Bookings')

    @api.multi
    def set_hours_before_send_notification_for_dedicated_bookings_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'hours_before_send_notification_for_dedicated_bookings', self.hours_before_send_notification_for_dedicated_bookings)

    @api.multi
    def set_booking_before_time_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'booking_before_time', self.booking_before_time)

    @api.multi
    def set_booking_after_time_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'booking_after_time', self.booking_after_time)

    @api.multi
    def set_action_needed_before_hours_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'action_needed_before_hours', self.action_needed_before_hours)

    @api.multi
    def set_reminder_sent_before_hours_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'reminder_sent_before_hours', self.reminder_sent_before_hours)

    @api.multi
    def set_send_notification_on_cancel_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'send_notification_on_cancel', self.send_notification_on_cancel)

    @api.multi
    def set_total_reminder_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'total_reminder', self.total_reminder)

    @api.multi
    def set_reminder_duration_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'reminder_duration', self.reminder_duration)

    @api.multi
    def set_delay_time_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'delay_time', self.delay_time)

    @api.multi
    def set_customer_booking_days_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'customer_booking_days', self.customer_booking_days)

    @api.multi
    def set_ot_start_time_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'ot_start_time', self.ot_start_time)

    @api.multi
    def set_ot_end_time_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'ot_end_time', self.ot_end_time)

    @api.multi
    def execute_configuration(self):
        return self.sudo().execute()


