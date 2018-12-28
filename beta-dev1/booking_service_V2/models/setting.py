# -*- coding: utf-8 -*-

from odoo import models, fields, api

class YourSettings(models.Model):
    _inherit = 'res.config.settings'
    _name = 'booking.settings'

    post_booking_time = fields.Integer('Post Booking Time')
    pre_booking_time  = fields.Integer('Pre Booking Time')

    @api.model
    def get_default_company_values(self, fields):
        """
        Method argument "fields" is a list of names
        of all available fields.
        """

        parameter_obj = self.env['ir.config_parameter']

        return {
            'post_booking_time': int(parameter_obj.get_param('booking.post_booking_time')) or 0,
            'pre_booking_time': int(parameter_obj.get_param('booking.pre_booking_time')) or 0
        }


    @api.one
    def set_company_values(self):
        parameter_obj = self.env['ir.config_parameter']

        parameter_obj.set_param('booking.post_booking_time', self.post_booking_time)
        parameter_obj.set_param('booking.pre_booking_time', self.pre_booking_time)

