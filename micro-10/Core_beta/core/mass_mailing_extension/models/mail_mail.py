# -*- coding: utf-8 -*-

import werkzeug.urls

from odoo import api, fields, models, tools

class MailMail(models.Model):
    _inherit = 'mail.mail'
    
    @api.multi
    def send_get_email_dict(self, partner=None):
        res = super(MailMail, self).send_get_email_dict(partner)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if self.mailing_id and res.get('body') and res.get('email_to'):
            emails = tools.email_split(res.get('email_to')[0])
            email_to = emails and emails[0] or False
            msg = 'Unsubscribe from this mailing list'
            unsubscribe_url = '<small><a href="%s">%s</a></small>' % ( self._get_unsubscribe_url(email_to), msg)
            if msg in res['body']:
                res['body'] = res['body'].replace(msg, unsubscribe_url if unsubscribe_url else '#')
        return res