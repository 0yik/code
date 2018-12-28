# -*- coding: utf-8 -*-

import pytz

from odoo import _, api, fields, models
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate
# from odoo.addons.report import render_report
from dateutil.relativedelta import relativedelta

class MailTemplate(models.Model):
	_inherit = "mail.template"
	_description = 'Email Templates'
	
	@api.multi
	def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None):
		"""Generates a new mail message for the given template and record,
		   and schedules it for delivery through the ``mail`` module's scheduler.

		   :param int res_id: id of the record to render the template with
							  (model is taken from the template)
		   :param bool force_send: if True, the generated mail.message is
				immediately sent after being created, as if the scheduler
				was executed for this message only.
		   :param dict email_values: if set, the generated mail.message is
				updated with given values dict
		   :returns: id of the mail.message that was created
		"""
		self.ensure_one()
		Mail = self.env['mail.mail']
		Attachment = self.env['ir.attachment']  # TDE FIXME: should remove dfeault_type from context

		# create a mail_mail based on values, without attachments
		values = self.generate_email(res_id)
		if isinstance(force_send, bool):
			values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]

		if isinstance(force_send, list):
			values['recipient_ids'] = [(4, pid) for pid in force_send]
			
		values.update(email_values or {})
		attachment_ids = values.pop('attachment_ids', [])
		attachments = values.pop('attachments', [])
		
		# add a protection against void email_from
		if 'email_from' in values and not values.get('email_from'):
			values.pop('email_from')
		mail = Mail.create(values)
		# manage attachments
		for attachment in attachments:
			if values.get('model') == 'crm.lead':
				attachment_data = {
					'name': attachment[0],
					'datas_fname': attachment[0],
					'datas': attachment[1],
					'res_model': 'mail.message',
					'res_id': mail.mail_message_id.id,
					'type':'binary'
				}
			if values.get('model') != 'crm.lead':
				attachment_data = {
					'name': attachment[0],
					'datas_fname': attachment[0],
					'datas': attachment[1],
					'res_model': 'mail.message',
					'res_id': mail.mail_message_id.id,
					}
			attachment_ids.append(Attachment.create(attachment_data).id)
		if attachment_ids:
			values['attachment_ids'] = [(6, 0, attachment_ids)]
			mail.write({'attachment_ids': [(6, 0, attachment_ids)]})

		if force_send:
			mail.send(raise_exception=raise_exception)
		return mail.id  # TDE CLEANME: return mail + api.returns ?

class crm_lead(models.Model):
	_inherit = 'crm.lead'

	dzh_partner_user_ids = fields.Many2many('dzh.partner.user','sol_dzh_partner_rel','sol_id','dzh_partner_id', string='User ID')

	@api.model
	def create(self, vals):
		res = super(crm_lead , self).create(vals)
		if 'dzh_check_box' in vals:
			if vals['dzh_check_box'] == True:
				template = self.env.ref('dzh_support_report.email_template_dzh_support_report', False)
				user_list = []
				for user in self.env['res.users'].search([('support_email','=',True)]):
					user_list.append(user.partner_id.id)
				template.send_mail(res.id,user_list)
		return res

	@api.multi
	def write(self, vals):
		if 'dzh_check_box' in vals:
			if vals['dzh_check_box'] == True:
				template = self.env.ref('dzh_support_report.email_template_dzh_support_report', False)
				user_list = []
				for user in self.env['res.users'].search([('support_email','=',True)]):
					user_list.append(user.partner_id.id)
				template.send_mail(self.id,user_list)
		return super(crm_lead , self).write(vals)

	@api.multi
	def notify_salesperson(self):
		for order in self:
			template = self.env.ref('dzh_support_report.email_template_dzh_trial_notification', False)
			template.send_mail(self.id)
		return True

class res_users(models.Model):
	_inherit = 'res.users'

	support_email = fields.Boolean('Support')
