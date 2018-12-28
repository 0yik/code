# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    attendance_server_host = fields.Char(string='Attendance Server Host')
    attendance_port = fields.Char(string='Attendance Server Port')
    attendance_username = fields.Char(string='Attendance Server Username')
    attendance_password = fields.Char(string='Attendance Server Password')
    attendance_file_location = fields.Char(string='Attendance Server File Location')
    attendance_file_name = fields.Char(string='Attendance Server File name')

    @api.multi
    def set_attendance_server_host_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'base.config.settings', 'attendance_server_host', self.attendance_server_host)

    @api.multi
    def set_attendance_port_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'base.config.settings', 'attendance_port', self.attendance_port)

    @api.multi
    def set_attendance_username_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'base.config.settings', 'attendance_username', self.attendance_username)

    @api.multi
    def set_attendance_password_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'base.config.settings', 'attendance_password', self.attendance_password)

    @api.multi
    def set_attendance_file_location_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'base.config.settings', 'attendance_file_location', self.attendance_file_location)

    @api.multi
    def set_attendance_file_name_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'base.config.settings', 'attendance_file_name', self.attendance_file_name)