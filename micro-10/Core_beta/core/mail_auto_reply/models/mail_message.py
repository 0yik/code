# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mail_message(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        res = super(mail_message, self).create(vals)
        if self._context.get('fetchmail_server_id',False) and not self._context.get('fetchmail_server_inbox',False) and not self._context.get('no_send_again',False):
            self = self.with_context(no_send_again=True)
            server = self.env['fetchmail.server'].sudo().browse(self._context.get('fetchmail_server_id'))
            if server.reply_template_id and server.reply_template_id.id:
                message_model = self.env['ir.model'].sudo().search([('model','=','mail.message')])
                server.reply_template_id.write({
                    'email_to': res.email_from or False,
                    'model_id': message_model.id,
                })
                server.reply_template_id.send_mail(False, force_send=True)
        return res