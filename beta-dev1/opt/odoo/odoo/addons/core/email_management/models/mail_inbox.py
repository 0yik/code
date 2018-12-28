# -*- coding: utf-8 -*-
from lxml import etree
import base64
import datetime
import logging
import psycopg2
import threading

from email.utils import formataddr, parseaddr

from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
from odoo.tools.safe_eval import safe_eval
from openerp.exceptions import except_orm, Warning
from email.utils import formataddr, parseaddr

_logger = logging.getLogger(__name__)


class vieterp_mail_inbox(models.Model):
    _inherit = 'mail.mail'
    _name = 'mail.inbox'

    @api.depends('recipient_ids', 'email_to')
    def _compute_recipient_to_text(self):
        for record in self:
            to_recipients = []
            if record.email_to and record.email_to != '':
                for email in record.email_to.split(','):
                    to_recipients.append(parseaddr(record.email_to)[1])
            if record.recipient_ids and len(record.recipient_ids) > 0:
                email_list = record.recipient_ids.mapped('email')
                for email in email_list:
                    if email:
                        to_recipients.append(email)
            if to_recipients != []:
                to_recipients = ', '.join(to_recipients)
                record.to_recipients = to_recipients

    fetchmail_server_id = fields.Many2one('fetchmail.server.inbox', "Inbound Mail Server", readonly=True, index=True,
                                          oldname='server_id')
    template_id = fields.Many2one('mail.template', string='Mail Template', select=True)
    recipient_ids = fields.Many2many('res.partner', relation='email_management_mail_recipient_partner_rel',
                                     column1='mail_id', column2='partner_id', string='To (Partners)')
    email_cc_partner = fields.Many2many('res.partner', relation='email_management_mail_cc_recipient_partner_rel',
                                        column1='mail_id', column2='partner_id', string="CC (Partners)")
    state = fields.Selection([
        ('inbox', 'Inbox'),
        ('outgoing', 'Outgoing'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('exception', 'Delivery Failed'),
        ('cancel', 'Cancelled'),
    ], 'Status', readonly=True, copy=False, default='outgoing')
    to_recipients = fields.Char('Recipients', compute=_compute_recipient_to_text)

    @api.model
    def create(self, vals):
        if vals.get('body_html', False) and not vals.get('body', False):
            vals['body'] = vals['body_html']
        res = super(vieterp_mail_inbox, self).create(vals)
        return res

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        self = self.with_context(default_user_id=False)
        author_id = False
        if self._context.get('fetchmail_server_id', False):
            server = self._context.get('fetchmail_server_id')
            user_mail = self.env['res.users'].sudo().search([('incomming_mail_server', '=', server)], limit=1)
            partner_id = user_mail.partner_id.id
        mail_data = {
            'subject': msg_dict.get('subject') or _("No Subject"),
            'email_from': msg_dict.get('from'),
            'email_to': msg_dict.get('to'),
            'email_cc': msg_dict.get('cc'),
            'author_id': partner_id,
            'partner_id': msg_dict.get('author_id', False),
            'body_html': msg_dict.get('body', ''),
            'attachment_ids': msg_dict.get('attachments', []),
            'state': 'inbox',
        }
        result = self.create(mail_data)
        return result.id

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        result = super(vieterp_mail_inbox, self).fields_view_get(view_id, view_type, toolbar, submenu)
        if view_type == 'form':
            try:
                current_id = context['params']['id']
            except:
                current_id = False
            my_state = self.browse(current_id).state
            if my_state in ['inbox', 'outgoing']:
                doc = etree.XML(result['arch'])
                for node in doc.xpath('//form'):
                    node.set('edit', 'true')
                result['arch'] = etree.tostring(doc)
        return result

    @api.onchange('template_id')  # if template are changed, call method
    def check_template_change(self):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values """
        if self.template_id and self.template_id.id:
            self.subject = self.template_id.subject
            self.body_html = self.template_id.body_html
            self.reply_to = self.template_id.reply_to
            self.mail_server_id = self.template_id.mail_server_id
            if self.template_id.attachment_ids:
                self.attachment_ids = [att.id for att in template.attachment_ids]
            if self.template_id.mail_server_id:
                self.mail_server_id = self.template_id.mail_server_id.id
            if self.template_id.user_signature and self.body_html:
                signature = self.env['res.users'].browse(self._uid).signature
                self.body = tools.append_content_to_html(self.body, signature, plaintext=False)
        else:
            if not self.body_html:
                signature = self.env['res.users'].browse(self._uid).signature
                self.body_html = signature

    @api.model
    def default_get(self, fields):
        res = super(vieterp_mail_inbox, self).default_get(fields)
        if self._context.get('button_message_res_id', False) and self._context.get('button_message_model', False):
            partner_obj = self.env['res.partner']
            res_id = self._context.get('button_message_res_id', False)
            model = self._context.get('button_message_model', False)
            model_obj = self.env[model].sudo().browse(res_id)
            if model_obj:
                follower_ids = [x.partner_id.id for x in model_obj.message_follower_ids]
                name = ''
                try:
                    name = model_obj.name_get()[0][1]
                except:
                    True
                res.update({
                    'recipient_ids': [(6, 0, follower_ids)],
                    'subject': name,
                })
            if model and model == 'helpdesk.ticket' and res_id:
                ticket_message_ids = model_obj.message_ids.sorted(key=lambda r: r.id)
                for ticket_message_id in ticket_message_ids:
                    if ticket_message_id.from_incomming_server and ticket_message_id.from_incomming_server.user and ticket_message_id.from_incomming_server.user != '':
                        res.update({
                            'email_from': ticket_message_id.from_incomming_server.user or '/',
                            'reply_to': ticket_message_id.from_incomming_server.user or '/',
                        })
                        break
                for message in model_obj.message_ids:
                    if message.from_incomming_server and message.from_incomming_server.id and message.message_type == 'email':
                        res.update({
                            'body_html': self.env.user.signature + '<br/>' + message.body ,
                            'attachment_ids': [(6, 0, [x.id for x in message.attachment_ids])],
                        })
                        break
                if model_obj.partner_email:
                    follower_ids = [x.partner_id.id for x in model_obj.message_follower_ids]
                    check_partner = self.env['res.partner'].search([('email','=', model_obj.partner_email),('id','in',follower_ids)])
                    if len(check_partner) == 0:
                        res.update({'email_to': model_obj.partner_email})
        return res

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
        server_email_line = self.env['ir.mail_server.email.line']
        default_outgoing = self.env['ir.mail_server']

        IrMailServer = self.env['ir.mail_server.outgoing']
        mail_server_id = False

        for mail_id in self.ids:
            try:
                mail = self.browse(mail_id)
                email_from = parseaddr(mail.email_from)[1]

                # Check Email From Helpdesk and check case for AWS ESE email

                if mail.model and mail.model == 'helpdesk.ticket' and mail.res_id:
                    try:
                        mail_server_ids = server_email_line.sudo().search([('name','=',email_from)]).mapped('server_id')
                        mail_server_id = mail_server_ids.sorted(key=lambda r: r.sequence)[0].id
                        IrMailServer = self.env['ir.mail_server']
                    except:
                        raise Warning('Please config Outgoing Mail for account %s'%(email_from))
                else:
                    if self._uid:
                        user_id = self.env['res.users'].browse(self._uid)
                        if user_id.outgoing_mail_server and user_id.outgoing_mail_server.id:
                            mail_server_id = user_id.outgoing_mail_server.id
                        mail_server_ids = server_email_line.sudo().search([('name', '=', email_from)]).mapped('server_id')
                        server_ids = mail_server_ids.sorted(key=lambda r: r.sequence)
                        if server_ids and len(server_ids) > 0:
                            mail_server_id = server_ids[0].id
                            IrMailServer = self.env['ir.mail_server']

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
                    email_list.append(mail.send_get_email_dict(partner=partner))

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
                headers['Return-Path'] = mail.email_from
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
                email_cc = ''
                if mail.email_cc:
                    email_cc = mail.email_cc
                if mail.email_cc_partner and len(mail.email_cc_partner) > 0:
                    for partner_id in mail.email_cc_partner:
                        if email_cc == '':
                            email_cc += partner_id.email or ''
                        else:
                            email_cc += ',' + partner_id.email or ''
                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                for email in email_list:
                    msg = IrMailServer.build_email(
                        email_from=mail.email_from,
                        email_to=email.get('email_to'),
                        subject=mail.subject,
                        body=email.get('body'),
                        body_alternative=email.get('body_alternative'),
                        email_cc=tools.email_split(email_cc),
                        reply_to=mail.reply_to,
                        attachments=attachments,
                        message_id=mail.message_id,
                        references=mail.references,
                        object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                        subtype='html',
                        subtype_alternative='plain',
                        headers=headers)
                    try:
                        res = IrMailServer.send_email(msg, mail_server_id=mail_server_id)
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
    def message_get_reply_to(self, res_ids, default=None):
        """ Returns the preferred reply-to email address that is basically the
        alias of the document, if it exists. Override this method to implement
        a custom behavior about reply-to for generated emails. """
        model_name = self.env.context.get('thread_model') or self._name
        alias_domain = self.env['ir.config_parameter'].get_param("mail.catchall.domain")
        res = dict.fromkeys(res_ids, False)

        # alias domain: check for aliases and catchall
        aliases = {}
        doc_names = {}
        if alias_domain:
            if model_name and model_name != 'mail.thread' and res_ids:
                mail_aliases = self.env['mail.alias'].sudo().search([
                    ('alias_parent_model_id.model', '=', model_name),
                    ('alias_parent_thread_id', 'in', res_ids),
                    ('alias_name', '!=', False)])
                # take only first found alias for each thread_id, to match
                # order (1 found -> limit=1 for each res_id)
                for alias in mail_aliases:
                    if alias.alias_parent_thread_id not in aliases:
                        aliases[alias.alias_parent_thread_id] = '%s@%s' % (alias.alias_name, alias_domain)
                doc_names.update(
                    dict((ng_res[0], ng_res[1])
                         for ng_res in self.env[model_name].sudo().browse(aliases.keys()).name_get()))
            # left ids: use catchall
            left_ids = set(res_ids).difference(set(aliases.keys()))
            if left_ids:
                catchall_alias = self.env['ir.config_parameter'].get_param("mail.catchall.alias")
                if catchall_alias:
                    aliases.update(dict((res_id, '%s@%s' % (catchall_alias, alias_domain)) for res_id in left_ids))
            # compute name of reply-to
            company_name = self.env.user.company_id.name
            for res_id in aliases.keys():
                email_name = '%s%s' % (company_name, doc_names.get(res_id) and (' ' + doc_names[res_id]) or '')
                email_addr = aliases[res_id]
                res[res_id] = formataddr((email_name, email_addr))
        left_ids = set(res_ids).difference(set(aliases.keys()))
        if left_ids:
            res.update(dict((res_id, default) for res_id in res_ids))
        return res

    @api.multi
    def reply_mail(self):
        ctx = {}
        signature = self.env['res.users'].browse(self._uid).signature or ''
        body_html = tools.append_content_to_html('', signature, plaintext=False)
        body_html = tools.append_content_to_html(body_html, self.body_html, plaintext=False)
        if self.email_from:
            ctx.update({
                'default_email_to': self.email_from,
                'default_subject': "Re: " + self.subject or "/",
                'default_body_html': body_html,
                'default_references': self.message_id,
                'form_view_ref': 'email_management.pop_up_compose_mail',
            })
        return {
            'name': 'Reply Email',
            'view_mode': 'form',
            'view_type': 'form',
            'context': ctx,
            'res_model': 'mail.inbox',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': False,
        }

    @api.multi
    def forward_mail(self):
        res = ''
        attachment_obj = self.env['ir.attachment']
        for rec in self:
            res = rec.copy()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.inbox',
            'view_mode': 'form',
            'target': 'current',
            'res_id': res.id,
            'flags': {'initial_mode': 'edit'},
            'context': self._context,
        }
