# -*- coding: utf-8 -*-

from odoo import models, fields, api

class fetchmail(models.Model):
    _inherit = 'fetchmail.server'

    reply_template_id = fields.Many2one('mail.template','Email Template')