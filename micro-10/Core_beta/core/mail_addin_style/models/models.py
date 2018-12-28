# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class mail_mass_mailing(models.Model):
    _inherit = 'mail.mass_mailing'

    body_html = fields.Text('HTML')
    raw_html  = fields.Text('Raw HTML')

    @api.multi
    def write(self, values):
        if values.get('raw_html', False):
            values.update({
                'body_html': values.get('raw_html')
            })
        result = super(mail_mass_mailing, self).write(values)
        return result

    @api.model
    def create(self, values):
        if values.get('raw_html', False):
            values.update({
                'body_html': values.get('raw_html')
            })
        result = super(mail_mass_mailing, self).create(values)
        return result