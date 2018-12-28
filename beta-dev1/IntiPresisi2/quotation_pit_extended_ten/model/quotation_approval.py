# -*- coding: utf-8 -*-
from odoo.osv.orm import setup_modifiers
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp
import logging
import psycopg2
from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import dateutil
import email
import hashlib
import hmac
import lxml
import logging
import pytz
import re
import socket
import time
import xmlrpclib

from collections import namedtuple
from email.message import Message
from email.utils import formataddr
from lxml import etree
from werkzeug import url_encode

from odoo import _, api, exceptions, fields, models, tools
from odoo.tools.safe_eval import safe_eval

class sign_line(models.Model):
	_name = 'sign.line'

	user_id = fields.Many2one('res.users','User')
	signature = fields.Binary('Signature')
	filename = fields.Char('filename')
	company_id = fields.Many2one('res.company','Company')

class res_company(models.Model):
	_inherit = 'res.company'

	sign_line_ids = fields.One2many('sign.line','company_id','Sign Line')

	def get_approved_image(self, obje, company):
		sign_obj = self.env['sign.line'].search([('user_id','=',obje.approved_by.id)])
		return sign_obj.signature

	def get_approved(self, obje):
		sign_obj = self.env['sign.line'].search([('user_id','=',obje.approved_by.id)])
		return sign_obj.user_id.name

class sale_order(models.Model):
	_inherit = 'sale.order'

	approved_by = fields.Many2one('res.users','User')
	state = fields.Selection([
		('draft', 'Quotation'),
		('sent', 'Quotation Sent'),
		('waiting_approval','Waiting For Approval'),
		('approved','Approved'),
		('sale', 'Sales Order'),
		('done', 'Locked'),
		('cancel', 'Cancelled'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

	def approv_quotation_send(self):
		recipient_list = []
		for sale in self:
			if self.company_id.sign_line_ids:
				for user in self.company_id.sign_line_ids:
					recipient_list.append(user.user_id.partner_id.id)
			action_id = self.env['ir.model.data'].get_object_reference('sale','action_quotations')[1]
			menu_id = self.env['ir.model.data'].get_object_reference('sale','menu_sale_quotations')[1]
			template = self.env.ref('quotation_pit_extended_ten.email_template_sale_order_approval_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
			mail_id = template.send_mail(self.id,recipient_list)
			self.env['mail.mail'].browse(mail_id).send()
			sale.write({'state':'waiting_approval'})

	@api.multi
	def action_quotation_send(self):
		'''
		This function opens a window to compose an email, with the edi sale template message loaded by default
		'''
		self.ensure_one()
		user_ids = []
		user_obj = self.env['res.users'].search([('sales_supervisor_b','=',True)])
		for ids in user_obj:
			user_ids.append(ids.partner_id.id)
		user_ids.append(self.partner_id.user_id.partner_id.id)
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = self.env.ref('quotation_pit_extended_ten.email_template_sale_order_approval_send', False)
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = dict()
		ctx.update({
			'default_model': 'sale.order',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id.id),
			'default_template_id': template_id.id,
			'default_composition_mode': 'comment',
			'default_email_cc_ids':[(6,0, user_ids)],
			'mark_so_as_sent': True,
			'mail_post_autofollow':False,
			'custom_layout': "sale.mail_template_data_notification_email_sale_order"
		})
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

class MailComposeMessage(models.TransientModel):
	_inherit = 'mail.compose.message'

	email_cc_ids = fields.Many2many('res.partner', 'mail_compose_message_res_partner_cc_rel', 'wizard_id', 'partner_cc_id', string='Email CC')
	email_bcc_ids = fields.Many2many('res.partner', 'mail_compose_message_res_partner_bcc_rel', 'wizard_id', 'partner_bcc_id', string='Email BCC')

	@api.multi
	def send_mail(self, auto_commit=False):
		if self._context.get('default_model') == 'sale.order' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
			order = self.env['sale.order'].browse([self._context['default_res_id']])
			order.state = 'sent'
			self = self.with_context(mail_post_autofollow=False)
		return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)

	@api.multi
	def get_mail_values(self, res_ids):
		res = super(MailComposeMessage, self).get_mail_values(res_ids)
		for key, value in res.iteritems():
			if self.email_bcc_ids:
				# value['email_bcc'] = wizard.email_bcc_ids[0].email
				value['email_bcc_ids'] = [(4, partner_bcc.id) for partner_bcc in self.email_bcc_ids]
			if self.email_cc_ids:
				# value['email_cc'] = wizard.email_cc_ids[0].email
				value['email_cc_ids'] = [(4, partner_cc.id) for partner_cc in self.email_cc_ids]
		return res


class Message(models.Model):
	_inherit = 'mail.message'

	email_cc_ids = fields.Many2many('res.partner', 'mail_notification_cc', 'message_id', 'partner_id', string='CC',
		help='Partners that have a notification pushing this message in their mailboxes')
	email_bcc_ids = fields.Many2many('res.partner', 'mail_notification_bcc', 'message_id', 'partner_id', string='BCC',
		help='Partners that have a notification pushing this message in their mailboxes')

	@api.multi
	def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
		""" Add the related record followers to the destination partner_ids if is not a private message.
			Call mail_notification.notify to manage the email sending
		"""
		group_user = self.env.ref('base.group_user')
		# have a sudoed copy to manipulate partners (public can go here with 
		# website modules like forum / blog / ...
		self_sudo = self.sudo()

		# TDE CHECK: add partners / channels as arguments to be able to notify a message with / without computation ??
		self.ensure_one()  # tde: not sure, just for testinh, will see
		partners = self.env['res.partner'] | self.partner_ids
		channels = self.env['mail.channel'] | self.channel_ids

		# all followers of the mail.message document have to be added as partners and notified
		# and filter to employees only if the subtype is internal
		if self_sudo.subtype_id and self.model and self.res_id:
			followers = self.env['mail.followers'].sudo().search([
				('res_model', '=', self.model),
				('res_id', '=', self.res_id)
			]).filtered(lambda fol: self.subtype_id in fol.subtype_ids)
			if self_sudo.subtype_id.internal:
				followers = followers.filtered(lambda fol: fol.channel_id or (fol.partner_id.user_ids and group_user in fol.partner_id.user_ids[0].mapped('groups_id')))
			channels = self_sudo.channel_ids | followers.mapped('channel_id')
			partners = self_sudo.partner_ids | followers.mapped('partner_id')
		else:
			channels = self_sudo.channel_ids
			partners = self_sudo.partner_ids

		# if self.email_cc_ids:
		#     partners |= self.email_cc_ids
		# if self.email_bcc_ids:
		#     partners |= self.email_bcc_ids

		# remove author from notified partners
		if not self._context.get('mail_notify_author', False) and self_sudo.author_id:
			partners = partners - self_sudo.author_id

		# update message, with maybe custom values
		message_values = {
			'channel_ids': [(6, 0, channels.ids)],
			'needaction_partner_ids': [(6, 0, partners.ids)]
		}
		if self.model and self.res_id and hasattr(self.env[self.model], 'message_get_message_notify_values'):
			message_values.update(self.env[self.model].browse(self.res_id).message_get_message_notify_values(self, message_values))
		self.write(message_values)
		# notify partners and channels
		partners._notify(self, force_send=force_send, send_after_commit=send_after_commit, user_signature=user_signature)
		channels._notify(self)

		# Discard cache, because child / parent allow reading and therefore
		# change access rights.
		if self.parent_id:
			self.parent_id.invalidate_cache()

		return True


class MailMail(models.Model):
	_inherit = 'mail.mail'

	email_bcc = fields.Char(string='Bcc', help='Black Carbon copy message recipients')

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

		for mail in self:
			try:
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
						headers['Return-Path'] = '%s+%d-%s-%d@%s' % (bounce_alias, mail.id, mail.model, mail.res_id, catchall_domain)
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
					'failure_reason': _('Error without exception. Probably due do sending an email without computed recipients.'),
				})
				mail_sent = False

				# build an RFC2822 email.message.Message object and send it without queuing
				res = None
				for email in email_list:
					msg = IrMailServer.build_email(
						email_from=mail.email_from,
						email_to=email.get('email_to'),
						subject=mail.subject,
						body=email.get('body'),
						body_alternative=email.get('body_alternative'),
						email_cc=tools.email_split(mail.email_cc),
						email_bcc=tools.email_split(mail.email_bcc),
						reply_to=mail.reply_to,
						attachments=attachments,
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

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _notify_prepare_email_values(self, message):
        mail_values = super(Partner, self)._notify_prepare_email_values(message)
        cc_email_list = message.email_cc_ids.mapped('email')
        bcc_email_list = message.email_bcc_ids.mapped('email')
        cc_bcc = {
            'email_cc': ",".join(cc_email_list),
            'email_bcc': ",".join(bcc_email_list),
        }
        mail_values.update(cc_bcc)
        return mail_values