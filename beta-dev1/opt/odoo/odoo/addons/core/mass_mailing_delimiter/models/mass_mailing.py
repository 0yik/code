# -*- coding: utf-8 -*-

import base64
import pickle
import json
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    Mail_Limit_Min = 150
    Mail_Action = 'send_mail'

    def send_mail(self):
        Mails = self.env['mail.mail']
        author_id = self.env.user.partner_id.id
        smtp_info = self.get_smtp_info()
        for mailing in self:
            # instantiate an email composer + send emails
            res_ids = mailing.get_remaining_recipients()
            if not res_ids:
                raise UserError(_('Please select recipients.'))

            # Convert links in absolute URLs before the application of the shortener
            mailing.body_html = self.env['mail.template']._replace_local_links(mailing.body_html)

            composer_values = {
                'author_id': author_id,
                'attachment_ids': [(4, attachment.id) for attachment in mailing.attachment_ids],
                'body': mailing.convert_links()[mailing.id],
                'subject': mailing.name,
                'model': mailing.mailing_model,
                'email_from': mailing.email_from,
                'record_name': False,
                'composition_mode': 'mass_mail',
                'mass_mailing_id': mailing.id,
                'mailing_list_ids': [(4, l.id) for l in mailing.contact_list_ids],
                'no_auto_thread': mailing.reply_to_mode != 'thread',
            }
            if mailing.reply_to_mode == 'email':
                composer_values['reply_to'] = mailing.reply_to

            composer = self.env['mail.compose.message'].with_context(active_ids=res_ids).create(composer_values)
            Mails += composer.with_context(active_ids=res_ids, mass_mailing_send_mail=True).send_mail(auto_commit=True)
            mailing.state = 'done'

            separate_data, general_data  = self.compute_mail_data(Mails)
            for separate_item in separate_data:
                self.env['mailing.queue'].send_message_action(self.Mail_Action, json.dumps({
                    'general': general_data,
                    'data': separate_item,
                    'smtp': smtp_info,
                }))
            for Mail in Mails:
                Mail.state = 'sent'
            # if smtp_attrs:
            #     multi_processing._multiprocessing_mass_mailing_min(msg_list, smtp_attrs)

        return True

    @api.model
    def get_mails(self):
        result = self.env['mailing.queue'].get_message_action(10, self.Mail_Action)
        return result

    @api.model
    def get_smtp_info(self):
        IrMailServer = self.env['ir.mail_server']
        mail_server = IrMailServer.sudo().search([], order='sequence', limit=1)
        if mail_server:
            return {
                'smtp_server' : mail_server.smtp_host,
                'smtp_port' : mail_server.smtp_port,
                'smtp_user' : mail_server.smtp_user,
                'smtp_password' : mail_server.smtp_pass,
                'smtp_encryption' : mail_server.smtp_encryption,
            }
        return False

    @api.model
    def compute_mail_data(self, mails):
        separate_data = []
        general_data = self.compute_mail_general_data(mails[0])
        for mail in mails:
            for res in self.compute_mail_separate_data(mail):
                separate_data.append(res)
        return [separate_data, general_data]

    @api.model
    def compute_mail_general_data(self, mail):
        attachments = [(a['datas_fname'], base64.b64decode(a['datas']))
                       for a in mail.attachment_ids.sudo().read(['datas_fname', 'datas'])]
        data = {
            'email_from': mail.email_from,
            'subject': mail.subject,
            'reply_to': mail.reply_to,
            'subtype': 'html',
            'attachments': attachments,
            'subtype_alternative': 'plain',
            'object_id': mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
        }
        return data

    @api.model
    def compute_mail_separate_data(self, mail):
        res = []
        # headers
        headers = {}
        bounce_alias = self.env['ir.config_parameter'].get_param("mail.bounce.alias")
        catchall_domain = self.env['ir.config_parameter'].get_param("mail.catchall.domain")
        if bounce_alias and catchall_domain:
            if mail.model and mail.res_id:
                headers['Return-Path'] = '%s+%d-%s-%d@%s' % (
                    bounce_alias, mail.id, mail.model, mail.res_id, catchall_domain)
            else:
                headers['Return-Path'] = '%s+%d@%s' % (bounce_alias, mail.id, catchall_domain)
        if mail.headers:
            try:
                headers.update(safe_eval(mail.headers))
            except Exception:
                pass

        email_list = []
        if mail.email_to:
            email_list.append(mail.send_get_email_dict())
        for partner in mail.recipient_ids:
            email_list.append(mail.send_get_email_dict(partner=partner))

        for email in email_list:
            msg = {
                'email_to': email.get('email_to'),
                'body': email.get('body'),
                'body_alternative': email.get('body_alternative'),
                'email_cc': tools.email_split(mail.email_cc),
                'message_id': mail.message_id,
                'references': mail.references,
                'headers': headers,
            }
            res.append(msg)
        return res

    @api.model
    def build_mail(self, datas):
        IrMailServer = self.env['ir.mail_server']
        res = []
        separate_data, simple_data  = datas
        for record in separate_data:
            msg_list = IrMailServer.build_email(
                email_from=simple_data.get('email_from'),
                email_to=record.get('email_to'),
                subject=simple_data.get('subject'),
                body=record.get('body'),
                body_alternative=record.get('body_alternative'),
                email_cc=record.get('email_cc'),
                reply_to=simple_data.get('reply_to'),
                attachments=simple_data.get('attachments'),
                message_id=record.get('message_id'),
                references=record.get('references'),
                object_id=simple_data.get('object_id'),
                subtype='html',
                subtype_alternative='plain',
                headers=record.get('headers'),
            )
            res.append(msg_list)
        return res