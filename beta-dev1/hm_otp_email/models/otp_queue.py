# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, SUPERUSER_ID

secret_key = '12313123123131'

class opt_link_queue(models.Model):

    _name = 'otp.link.queue'
    _inherit = ['mail.thread']

    mail_id = fields.Char(string="Mail Id")
    attachment_id = fields.Char(string="Attachment Id")
    token = fields.Integer(string="Token", compute='_generate_token')
    partner_id = fields.Many2one('res.partner', string="Partner")
    email_to = fields.Char(string='Email')

    def _generate_token(self):
        for record in self:
            hashed = record.generate_token()
            record.token = hashed

    def generate_token(self):
        timestamp = int(int(datetime.datetime.now().strftime('%Y%m%d%H%M')) / 30)
        hash_string = '%s%s%s' %(secret_key, self.id, timestamp)
        hashed = abs(hash(hash_string)) % (10 ** 8);
        return hashed

    def verify_token(self, token):
        if int(token) == self.generate_token():
            return True
        return False


    def send_email(self):
        template_email = self.env.ref('hm_otp_email.email_template_token_notify')

        recipients = []
        if self.create_uid and self.create_uid.partner_id:
            recipients.append(self.create_uid.partner_id.id)

        if recipients:
            if template_email:
                template_email.send_mail(self.id, force_send=True)
        return True

    def download_attachment(self):
        """ Return the content of linked attachments. """
        # this will fail if you cannot read the message
        message_obj = self.env['mail.message']
        attachment_id = int(self.attachment_id)

        attachment = self.env['ir.attachment'].browse(attachment_id)
        if attachment.datas and attachment.datas_fname:
            return {
                'base64': attachment.datas,
                'filename': attachment.datas_fname,
            }

        return False