# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class TestMassMailing(models.TransientModel):
    _inherit = 'mail.mass_mailing.test'

    @api.multi
    def send_mail_test(self):
        self.ensure_one()
        mailing = self.mass_mailing_id
        test_emails = tools.email_split(self.email_to)
        for test_mail in test_emails:
            mailing.write({'body_html': self.env['mail.template']._replace_local_links(mailing.body_html)})
            mail_values = {
                'email_from': mailing.email_from,
                'reply_to': mailing.reply_to,
                'email_to': test_mail,
                'subject': mailing.name,
                'body_html': '',
                'notification': True,
                'mailing_id': mailing.id,
                'attachment_ids': [(4, attachment.id) for attachment in mailing.attachment_ids],
            }
            mail = self.env['mail.mail'].create(mail_values)
            unsubscribe_url = mail._get_unsubscribe_url(test_mail)
            body = tools.append_content_to_html(mailing.body_html, unsubscribe_url, plaintext=False, container_tag='p')
            mail.write({'body_html': body})
        return True
