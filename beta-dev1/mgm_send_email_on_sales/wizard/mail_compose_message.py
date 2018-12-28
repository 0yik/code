import base64

from odoo import _, api, fields, models, SUPERUSER_ID, tools


class MailComposer(models.TransientModel):

    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):

        result = super(MailComposer, self).default_get(fields)

        result['menu_id'] = result.get('menu_id', self._context.get('menu_id'))
        result['action_id'] = result.get('action_id', self._context.get('action_id'))

        return result

    employee_ids = fields.Many2many('hr.employee', 'mail_compose_hr_employee_rel', 'wizard_id', 'employee_id', 'Additional Contacts' )
    menu_id = fields.Many2one('ir.ui.menu', 'Menu')
    action_id = fields.Many2one('ir.actions.actions', 'Action')

    @api.model
    def get_record_data(self, values):

        result, subject = {}, False
        if values.get('parent_id'):
            parent = self.env['mail.message'].browse(values.get('parent_id'))
            result['record_name'] = parent.record_name,
            subject = tools.ustr(parent.subject or parent.record_name or '')
            if not values.get('model'):
                result['model'] = parent.model
            if not values.get('res_id'):
                result['res_id'] = parent.res_id

            partner_ids = values.get('partner_ids', list()) + [(4, id) for id in parent.partner_ids.ids]
            if self._context.get(
                    'is_private') and parent.author_id:  # check message is private then add author also in partner list.
                partner_ids += [(4, parent.author_id.id)]
            if not values.get('menu_id') and not values.get('action_id'):
                result['partner_ids'] = partner_ids
        elif values.get('model') and values.get('res_id'):
            doc_name_get = self.env[values.get('model')].browse(values.get('res_id')).name_get()
            result['record_name'] = doc_name_get and doc_name_get[0][1] or ''
            subject = tools.ustr(result['record_name'])

        re_prefix = _('Re:')
        if subject and not (subject.startswith('Re:') or subject.startswith(re_prefix)):
            subject = "%s %s" % (re_prefix, subject)
        result['subject'] = subject

        return result

    @api.multi
    def get_mail_values(self, res_ids):
        self.ensure_one()
        results = dict.fromkeys(res_ids, False)
        rendered_values = {}
        mass_mail_mode = self.composition_mode == 'mass_mail'

        if mass_mail_mode and self.model:
            rendered_values = self.render_message(res_ids)
        reply_to_value = dict.fromkeys(res_ids, None)
        if mass_mail_mode and not self.no_auto_thread:
            reply_to_value = self.env['mail.thread'].with_context(thread_model=self.model).message_get_reply_to(res_ids,
                                                                                                                 default=self.email_from)
        for res_id in res_ids:
            mail_values = {
                'subject': self.subject,
                'body': self.body or '',
                'parent_id': self.parent_id and self.parent_id.id,
                'partner_ids': [partner.id for partner in self.partner_ids] + [employee.user_id.partner_id.id for employee in self.employee_ids],
                'attachment_ids': [attach.id for attach in self.attachment_ids],
                'author_id': self.author_id.id,
                'email_from': self.email_from,
                'record_name': self.record_name,
                'no_auto_thread': self.no_auto_thread,
                'mail_server_id': self.mail_server_id.id,
            }

            # mass mailing: rendering override wizard static values
            if mass_mail_mode and self.model:
                if self.model in self.env and hasattr(self.env[self.model], 'message_get_email_values'):
                    mail_values.update(self.env[self.model].browse(res_id).message_get_email_values())
                # keep a copy unless specifically requested, reset record name (avoid browsing records)
                mail_values.update(notification=not self.auto_delete_message, model=self.model, res_id=res_id,
                                   record_name=False)
                # auto deletion of mail_mail
                if self.auto_delete or self.template_id.auto_delete:
                    mail_values['auto_delete'] = True
                # rendered values using template
                email_dict = rendered_values[res_id]
                mail_values['partner_ids'] += email_dict.pop('partner_ids', [])
                mail_values.update(email_dict)
                if not self.no_auto_thread:
                    mail_values.pop('reply_to')
                    if reply_to_value.get(res_id):
                        mail_values['reply_to'] = reply_to_value[res_id]
                if self.no_auto_thread and not mail_values.get('reply_to'):
                    mail_values['reply_to'] = mail_values['email_from']
                # mail_mail values: body -> body_html, partner_ids -> recipient_ids
                mail_values['body_html'] = mail_values.get('body', '')
                mail_values['recipient_ids'] = [(4, id) for id in mail_values.pop('partner_ids', [])]

                # process attachments: should not be encoded before being processed by message_post / mail_mail create
                mail_values['attachments'] = [(name, base64.b64decode(enc_cont)) for name, enc_cont in
                                              email_dict.pop('attachments', list())]
                attachment_ids = []
                for attach_id in mail_values.pop('attachment_ids'):
                    new_attach_id = self.env['ir.attachment'].browse(attach_id).copy(
                        {'res_model': self._name, 'res_id': self.id})
                    attachment_ids.append(new_attach_id.id)
                mail_values['attachment_ids'] = self.env['mail.thread']._message_preprocess_attachments(
                    mail_values.pop('attachments', []),
                    attachment_ids, 'mail.message', 0)
            results[res_id] = mail_values
        return results

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'sale.order' and self._context.get('default_res_id'):
            order = self.env['sale.order'].browse([self._context['default_res_id']])
            if order.state == 'draft' and self.action_id:
                order.state = 'so_sent'
            order.vals_update = False
        return super(MailComposer, self).send_mail(auto_commit=auto_commit)
