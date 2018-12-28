# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    use_in_marketing_automation = fields.Boolean(
        string='Specific mailing used in marketing campaign', default=False,
        help='Marketing campaigns use mass mailings with some specific behavior; this field is used to indicate its statistics may be suspicious.')

    def convert_links(self):
        res = {}
        done = self.env['mail.mass_mailing']
        for mass_mailing in self:
            if self.env.context.get('default_marketing_activity_id'):
                activity = self.env['marketing.automation.activity'].browse(self.env.context['default_marketing_activity_id'])
                vals = {
                    'mass_mailing_id': self.id,
                    'campaign_id': activity.campaign_id.utm_campaign_id.id,
                    'source_id': activity.utm_source_id.id,
                    'medium_id': self.medium_id.id,
                }
                res[mass_mailing.id] = self.env['link.tracker'].convert_links(
                    self.body_html or '',
                    vals,
                    blacklist=['/unsubscribe_from_list']
                )
                done |= mass_mailing
        res.update(super(MassMailing, self - done).convert_links())
        return res

    def send_mail(self):
        if self._context.get('default_marketing_activity_id'):
            author_id = self.env.user.partner_id.id
            for mailing in self:
                # instantiate an email composer + send emails
                res_ids = self._context.get('active_ids')
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
                composer.with_context(active_ids=res_ids).send_mail(auto_commit=True)
                mailing.state = 'done'
            return True
        return super(MassMailing, self).send_mail()
