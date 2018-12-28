# -*- coding: utf-8 -*-

from odoo import models, fields, api

class booking_setting_reusable(models.TransientModel):
    _inherit = 'booking.settings'

    block_by_worker = fields.Boolean(string='Block the date and time from being booked if the employee is booked already (Not Available)')
    blook_by_equipment = fields.Boolean(string='Block the date and time from being booked  if the equipment is booked already (Not Available)')

    @api.model
    def get_default_company_values(self, fields):
        """
        Method argument "fields" is a list of names
        of all available fields.
        """

        parameter_obj = self.env['ir.config_parameter']

        return {
            'post_booking_time': int(parameter_obj.get_param('booking.post_booking_time')) or 0,
            'pre_booking_time': int(parameter_obj.get_param('booking.pre_booking_time')) or 0,
            'block_by_worker' : parameter_obj.get_param('booking.block_by_worker') or False,
            'blook_by_equipment' : parameter_obj.get_param('booking.blook_by_equipment') or False,
        }

    @api.one
    def set_company_values(self):
        parameter_obj = self.env['ir.config_parameter']

        parameter_obj.set_param('booking.post_booking_time', self.post_booking_time)
        parameter_obj.set_param('booking.pre_booking_time', self.pre_booking_time)
        parameter_obj.set_param('booking.block_by_worker', self.block_by_worker)
        parameter_obj.set_param('booking.blook_by_equipment', self.blook_by_equipment)
