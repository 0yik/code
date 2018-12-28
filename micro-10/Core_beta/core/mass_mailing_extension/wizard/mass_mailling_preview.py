# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MassMailingPreview(models.TransientModel):
    _inherit = "mail.mass_mailing"
    _name = "mass_mailing.preview"
    # _description = "Email Template Preview"

    @api.model
    def _get_records(self):
        """ Return Records of particular Email Template's Model """
        template_id = self._context.get('template_id')
        default_res_id = self._context.get('default_res_id')
        if not template_id:
            return []
        template = self.env['mail.template'].browse(int(template_id))
        records = self.env[template.model_id.model].search([], limit=10)
        records |= records.browse(default_res_id)
        return records.name_get()

    @api.model
    def default_get(self, fields):
        result = super(MassMailingPreview, self).default_get(fields)
        if self._context.get('active_id'):
            mass_mail_id = self.env['mail.mass_mailing'].browse(self._context.get('active_id'))
            result['body'] = mass_mail_id.body_html
            result['name'] = mass_mail_id.name
            result['email_from'] = mass_mail_id.email_from
            result['mailing_model'] = mass_mail_id.mailing_model
            if mass_mail_id.mailing_model == 'mail.mass_mailing.contact':
                result['contact_list_ids'] = mass_mail_id.contact_list_ids.ids
            result['keep_archives'] = mass_mail_id.keep_archives
            result['reply_to'] = mass_mail_id.reply_to
            result['scheduled'] = mass_mail_id.scheduled
            result['attachment_ids'] = mass_mail_id.attachment_ids.ids

        if 'res_id' in fields and not result.get('res_id'):
            records = self._get_records()
            result['res_id'] = records and records[0][0] or False  # select first record as a Default
        if self._context.get('template_id') and 'model_id' in fields and not result.get('model_id'):
            result['model_id'] = self.env['mail.template'].browse(self._context['template_id']).model_id.id
        
        return result

    body = fields.Html(string="Body")
    res_id = fields.Selection(_get_records, 'Sample Document')
    partner_ids = fields.Many2many('res.partner', string='Recipients')
