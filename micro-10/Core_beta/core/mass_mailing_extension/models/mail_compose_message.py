# -*- coding: utf-8 -*-

from odoo import  fields, models

class MailComposer(models.TransientModel):

    _inherit = 'mail.compose.message'

    body = fields.Html('Contents', default='', sanitize_style=False, strip_classes=False)