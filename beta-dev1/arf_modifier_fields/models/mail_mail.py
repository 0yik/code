# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo.tools.safe_eval import safe_eval
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
from odoo.addons.website.models.website import slug
from datetime import date
import logging

import base64
import logging
import psycopg2

from odoo import api, fields, models, _
import odoo.tools as tools
_logger = logging.getLogger(__name__)

class mail_mail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        result = super(mail_mail, self).send(auto_commit=auto_commit, raise_exception=raise_exception)
        # for record in self:
        #     if record.res_id and record.model == 'helpdesk.ticket':
        #         history_data = {
        #             'ticket_id': record.res_id,
        #             'subject': record.subject,
        #             'body': record.body_html,
        #             'date': fields.Date.today(),
        #             'status': record.state,
        #         }
        #         self.env['helpdesk.ticket.email'].create(history_data)
        return result



class mail_inbox(models.Model):
    _inherit = 'mail.inbox'

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        """ Sends the selected emails immediately, ignoring their current
            state (mails that have already been sent should not be passed
            unless they should actually be re-sent).
            Emails successfully delivered are marked as 'sent', and those
            that fail to be deliver are marked as 'exception', and the
            corresponding error mail is output in the server logs.

            :param bool auto_commit: whether to force a commit of the mail status
                after sending each mail (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param bool raise_exception: whether to raise an exception if the
                email sending process has failed
            :return: True
        """
        IrMailServer = self.env['ir.mail_server']
        domain_link = self.env['ir.config_parameter'].get_param('web.base.url')
        for mail_id in self.ids:
            try:
                mail = self.browse(mail_id)
                # TDE note: remove me when model_id field is present on mail.message - done here to avoid doing it multiple times in the sub method
                if mail.model:
                    model = self.env['ir.model'].sudo().search([('model', '=', mail.model)])[0]
                else:
                    model = None
                if model:
                    mail = mail.with_context(model_name=model.name)

                # load attachment binary data with a separate read(), as prefetching all
                # `datas` (binary field) could bloat the browse cache, triggerring
                # soft/hard mem limits with temporary data.
                attachments = [(a['datas_fname'], base64.b64decode(a['datas']))
                               for a in mail.attachment_ids.sudo().read(['datas_fname', 'datas'])]

                # specific behavior to customize the send email for notified partners
                email_list = []
                if mail.email_to:
                    email_list.append(mail.send_get_email_dict())
                for partner in mail.recipient_ids:
                    email_data = mail.send_get_email_dict(partner=partner)
                    email_data.update({'partner_id': partner.id})
                    email_list.append(email_data)

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

                # Writing on the mail object may fail (e.g. lock on user) which
                # would trigger a rollback *after* actually sending the email.
                # To avoid sending twice the same email, provoke the failure earlier
                mail.write({
                    'state': 'exception',
                    'failure_reason': _(
                        'Error without exception. Probably due do sending an email without computed recipients.'),
                })
                mail_sent = False

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                for email in email_list:
                    body = email.get('body')
                    for attachment in mail.attachment_ids:
                        data = {
                            'mail_id': mail.id,
                            'crete_uid': 1,
                            'attachment_id': str(attachment.id),
                            'partner_id': email.get('partner_id'),
                            'email_to': email.get('email_to') and email.get('email_to')[0] or False,

                        }
                        queue = self.env['otp.link.queue'].create(data)
                        link_download = domain_link + '''/otp/download/%s''' % str(queue.id)
                        fname = attachment.datas_fname or ''
                        body += "\n<a href='" + link_download + """' style='display: inline-block;
                                margin-top: 8px;
                                white-space: nowrap;
                                padding: 6px 15px;
                                font-size: 14px;
                                line-height: 1.42857143;
                                border-radius: 2px;
                                text-decoration: none;
                                color: #fff;
                                border-color: #21b799;
                                background-color: #21b799;
                                font-weight:bold'>Click to download """ + fname + "</a><br/>"

                    msg = IrMailServer.build_email(
                        email_from=mail.email_from,
                        email_to=email.get('email_to'),
                        subject=mail.subject,
                        body=body,
                        body_alternative=email.get('body_alternative'),
                        email_cc=tools.email_split(mail.email_cc),
                        reply_to=mail.reply_to,
                        # attachments=attachments,
                        message_id=mail.message_id,
                        references=mail.references,
                        object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                        subtype='html',
                        subtype_alternative='plain',
                        headers=headers)
                    try:
                        res = IrMailServer.send_email(msg, mail_server_id=mail.mail_server_id.id)
                    except AssertionError as error:
                        if error.message == IrMailServer.NO_VALID_RECIPIENT:
                            # No valid recipient found for this particular
                            # mail item -> ignore error to avoid blocking
                            # delivery to next recipients, if any. If this is
                            # the only recipient, the mail will show as failed.
                            _logger.info("Ignoring invalid recipients for mail.mail %s: %s",
                                         mail.message_id, email.get('email_to'))
                        else:
                            raise
                if res:
                    mail.write({'state': 'sent', 'message_id': res, 'failure_reason': False})
                    mail_sent = True
                # /!\ can't use mail.state here, as mail.refresh() will cause an error
                # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                if mail_sent:
                    _logger.info('Mail with ID %r and Message-Id %r successfully sent', mail.id, mail.message_id)
                mail._postprocess_sent_message(mail_sent=mail_sent)
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                _logger.exception(
                    'MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option',
                    mail.id, mail.message_id)
                raise
            except psycopg2.Error:
                # If an error with the database occurs, chances are that the cursor is unusable.
                # This will lead to an `psycopg2.InternalError` being raised when trying to write
                # `state`, shadowing the original exception and forbid a retry on concurrent
                # update. Let's bubble it.
                raise
            except Exception as e:
                failure_reason = tools.ustr(e)
                _logger.exception('failed sending mail (id: %s) due to %s', mail.id, failure_reason)
                mail.write({'state': 'exception', 'failure_reason': failure_reason})
                mail._postprocess_sent_message(mail_sent=False)
                if raise_exception:
                    if isinstance(e, AssertionError):
                        # get the args of the original error, wrap into a value and throw a MailDeliveryException
                        # that is an except_orm, with name and value as arguments
                        value = '. '.join(e.args)
                        raise MailDeliveryException(_("Mail Delivery Failed"), value)
                    raise

            if auto_commit is True:
                self._cr.commit()
        return True

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        self = self.with_context(default_user_id=False)
        author_id = False
        attachments = []
        if self._context.get('fetchmail_server_id', False):
            server = self._context.get('fetchmail_server_id')
            user_mail = self.env['res.users'].sudo().search([('incomming_mail_server', '=', server)], limit=1)
            partner_id = user_mail.partner_id.id
            if msg_dict.get('attachments', []):
                for attachment in msg_dict.get('attachments', []):
                    attach_data = {
                        'name': attachment.fname,
                        'datas_fname': attachment.fname,
                        'datas': base64.encodestring(attachment.content),
                        'res_model': 'mail.inbox',
                        'type': 'binary',
                        'res_id': 0,
                    }
                    ir_att = self.env['ir.attachment'].create(attach_data)
                    attachments.append(ir_att.id)
        if attachments:
            mail_data = {
                'subject': msg_dict.get('subject') or _("No Subject"),
                'email_from': msg_dict.get('from'),
                'email_to': msg_dict.get('to'),
                'email_cc': msg_dict.get('cc'),
                'author_id': partner_id,
                'partner_id': msg_dict.get('author_id', False),
                'body_html': msg_dict.get('body', ''),
                'attachment_ids': [(6, 0, attachments)],
                'state': 'inbox',
            }
        else:
            mail_data = {
                'subject': msg_dict.get('subject') or _("No Subject"),
                'email_from': msg_dict.get('from'),
                'email_to': msg_dict.get('to'),
                'email_cc': msg_dict.get('cc'),
                'author_id': partner_id,
                'partner_id': msg_dict.get('author_id', False),
                'body_html': msg_dict.get('body', ''),
                'state': 'inbox',
            }
        result = self.create(mail_data)
        return result.id

    @api.model
    def default_get(self, fields):
        res = super(mail_inbox, self).default_get(fields)
        if self._context.get('body_html'):
            res.update({
                'body_html': self._context.get('body_html'),
                'subject': self._context.get('subject')
            })
        return res


class mail_message_inherit(models.Model):
    _inherit = 'mail.message'

    check_user = fields.Boolean(string="Check Customer", default=False)
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            subject = record.id
            res.append((record['id'], str(subject)))
        return res
    @api.model
    def create(self, vals):
        res = super(mail_message_inherit, self).create(vals)
        print "vals---->>", vals
        if 'body' in vals.keys():
            if 'model' in vals.keys():
                if vals['model'] == 'helpdesk.ticket':
                    history_data = {
                        'ticket_id': vals['res_id'],
                        'email_id': res.id,
                        'subject': vals['subject'],
                        'body': vals['body'],
                        'date': vals['date'] or fields.Date.today(),
                        'date': fields.Date.today(),
                        'status': '',
                    }
                    self.env['helpdesk.ticket.email'].create(history_data)
            # except:
            #     history_data = {
            #         'email_id': res.id,
            #         'subject': vals['subject'],
            #         'body': vals['body'],
            #         'date': fields.Date.today(),
            #         'date': fields.Date.today(),
            #         'status': '',
            #     }

        return res




class mail_thread_inherit(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        data = {}
        if isinstance(custom_values, dict):
            data = custom_values.copy()
        model = self._context.get('thread_model') or self._name
        if model == 'helpdesk.ticket':
            if data.get('partner_id'):
                partner = self.env['res.partner'].browse(data.get('partner_id'))
                data_ticket = {
                    'name':             msg_dict.get('subject', ''),
                    # 'customer_name':    partner.id,
                    'partner_id'        : partner.id,
                    'employer_name':    partner.name_employer,
                    'company_name':     partner.name,
                    'contract_person':  partner.contract_person,
                    'contract_mobile':  int(partner.contract_mobile),
                    'contract_hom':     int(partner.contract_hom),
                    'contract_work':    int(partner.contract_mobile),
                    'email':            partner.email,
                    'nature_of_business': partner.nature_of_busines,
                    'nric_fin':         partner.nric_passport_ros,
                    'passpost_no':      0,
                    'nationality':      partner.nationality.id,
                    'age':              partner.age,
                    'gender':           partner.gender,
                    # 'date_birth':       datetime.strptime( partner.date_birth, '%Y-%m-%d').date(),
                    'marital_status':   partner.marital_status,
                    'occupation':       partner.occupation,
                    # 'license_pass_date': datetime.strptime(partner.lic_part_date, '%Y-%m-%d').date(),
                    'postal_code':      partner.postal_code,
                }
                RecordModel = self.env[model]
                res = RecordModel.create(data_ticket)
                mail_data = {
                    'model': 'mail.inbox',
                    'subject': msg_dict.get('subject') or _("No Subject"),
                    'email_from': msg_dict.get('from'),
                    'email_to': msg_dict.get('to'),
                    'email_cc': msg_dict.get('cc'),
                    'author_id': self.env['res.users'].browse(self._uid).partner_id.id,
                    'body_html': msg_dict.get('body', ''),
                    'state': 'inbox',
                }
                self.env['mail.inbox'].create(mail_data)
                return res.id
        RecordModel = self.env[model]
        fields = RecordModel.fields_get()
        name_field = RecordModel._rec_name or 'name'
        if name_field in fields and not data.get('name'):
            data[name_field] = msg_dict.get('subject', '')
            data['email'] = msg_dict.get('email_from', '')
        res = RecordModel.create(data)
        mail_data = {
            'model': 'mail.inbox',
            'subject': msg_dict.get('subject') or _("No Subject"),
            'email_from': msg_dict.get('from'),
            'email_to': msg_dict.get('to'),
            'email_cc': msg_dict.get('cc'),
            'author_id': self.env['res.users'].browse(self._uid).partner_id.id,
            'body_html': msg_dict.get('body', ''),
            'state': 'inbox',
        }
        self.env['mail.inbox'].create(mail_data)
        return res.id
