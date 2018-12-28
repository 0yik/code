# -*- coding: utf-8 -*-

import urlparse
import datetime

from odoo import api, fields, models, tools


class BaseConfiguration(models.TransientModel):

    _inherit = 'base.config.settings'

    activate_password_validation = fields.Boolean(string='Activate the password validation')
    allowed_login_attempts = fields.Char(string='Allowed Login Attempts')
    activate_minimum_password_length = fields.Boolean(string='Activate minimum password length')
    minimum_password_length = fields.Char(string='Characters Minimum')
    password_complexity = fields.Boolean(string='Password Complexity')
    password_history = fields.Boolean(string='Password History')
    activate_password_change_reminder = fields.Boolean(string='Activate password change reminder')
    change_reminder_days = fields.Char(string='Days (It is advisable to set it to 90 days for security purposes)')
    password_change_upon_initial_logon = fields.Boolean(string='Password change upon initial logon')

    @api.model
    def get_default_password_change_upon_initial_logon(self, fields):
        return {'password_change_upon_initial_logon': self.env["ir.config_parameter"].get_param("password_change_upon_initial_logon")}

    @api.multi
    def set_password_change_upon_initial_logon(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("password_change_upon_initial_logon", record.password_change_upon_initial_logon)

    @api.model
    def get_default_activate_password_change_reminder(self, fields):
        return {'activate_password_change_reminder': self.env.ref("password_validation_security.password_change_reminder").active}

    @api.multi
    def set_activate_password_change_reminder(self):
        for record in self:
            self.env.ref("password_validation_security.password_change_reminder").active = record.activate_password_change_reminder
    
    @api.model
    def get_default_change_reminder_days(self, fields):
        return {'change_reminder_days': self.env["ir.config_parameter"].get_param("change_reminder_days")}

    @api.multi
    def set_change_reminder_days(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("change_reminder_days", record.change_reminder_days)

    @api.model
    def get_default_password_history(self, fields):
        return {'password_history': self.env["ir.config_parameter"].get_param("password_history")}

    @api.multi
    def set_password_history(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("password_history", record.password_history)
    
    @api.model
    def get_default_password_complexity(self, fields):
        return {'password_complexity': self.env["ir.config_parameter"].get_param("password_complexity")}

    @api.multi
    def set_password_complexity(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("password_complexity", record.password_complexity)
    
    @api.model
    def get_default_activate_minimum_password_length(self, fields):
        return {'activate_minimum_password_length': self.env["ir.config_parameter"].get_param("activate_minimum_password_length")}

    @api.multi
    def set_activate_minimum_password_length(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("activate_minimum_password_length", record.activate_minimum_password_length)
    
    @api.model
    def get_default_minimum_password_length(self, fields):
        return {'minimum_password_length': self.env["ir.config_parameter"].get_param("minimum_password_length")}

    @api.multi
    def set_minimum_password_length(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("minimum_password_length", record.minimum_password_length)

    @api.model
    def get_default_activate_password_validation(self, fields):
        return {'activate_password_validation': self.env["ir.config_parameter"].get_param("activate_password_validation")}

    @api.multi
    def set_activate_password_validation(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("activate_password_validation", record.activate_password_validation)
            
    
    @api.model
    def get_default_allowed_login_attempts(self, fields):
        return {'allowed_login_attempts': self.env["ir.config_parameter"].get_param("allowed_login_attempts")}

    @api.multi
    def set_allowed_login_attempts(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("allowed_login_attempts", record.allowed_login_attempts)
