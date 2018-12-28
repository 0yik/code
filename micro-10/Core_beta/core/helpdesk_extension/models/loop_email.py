# -*- coding: utf-8 -*-

from odoo import models, fields, api

class add_email(models.Model):
    _name = 'loop.email'

    name = fields.Char('Email')


class mail_incoming(models.Model):
    _inherit = 'mail.message'

    mail_incoming = fields.Many2one('fetchmail.server')