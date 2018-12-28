from odoo import models, fields, api

class Meeting(models.Model):
    _inherit = 'calendar.event'

    is_commited = fields.Boolean('Is committed', default=False)

    @api.model
    def create(self, vals):
        if vals.get('start_date') or vals.get('start_datetime')or vals.get('location'):
            vals.update({'is_commited': True})
        return super(Meeting, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('start_date') or vals.get('start_datetime') or vals.get('location'):
            vals.update({'is_commited': True})
        return super(Meeting, self).write(vals)

    def _meeting_summary_remainder_scheduler(self):
        missing_summary_ids = []
        all_event = self.search([])
        attachement_search_ids = [x.res_id for x in self.env['ir.attachment'].search([('res_model', '=', 'calendar.event')])]
        for event in all_event:
            if event.id not in attachement_search_ids:
                missing_summary_ids.append(event.id)
        description_missings = self.search([('description', '=', False)]).ids
        missing_summary_ids += description_missings

        for i in set(missing_summary_ids):
            event_br = self.browse(i)
            recipients = [x.name for x in event_br.partner_ids]
            recipients_name = ', '.join(recipients)
            mail_content = 'Hi ', recipients_name,  ',<br>A gentle reminder to update Meeting Summary or attach your meeting notes in meeting calendar.',\
            '<br><b>Meeting Subject  : </b>', event_br.name,\
            '<br><b>Meeting Date  : </b>', event_br.start_date and event_br.start_date or event_br.start_datetime,\
            '<br><b>Location  : </b>', event_br.location, \
            '<br>Thank you. Have a wonderful day ahead.'
            for user in event_br.partner_ids:
                main_content = {
                    'subject': 'Meeting Summary Reminder',
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': user.email,
                }
                self.env['mail.mail'].create(main_content).send()

