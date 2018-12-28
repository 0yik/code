from odoo import api, fields, models, _

class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def _get_email_count(self):
        for record in self:
            record.email_count = self.env['mail.inbox'].sudo().search_count([('crm_lead_id','=',self.id)])

    email_count = fields.Integer(compute='_get_email_count', string='Emails')

    @api.multi
    def action_emails(self):
        action = self.env.ref('email_management.action_mail_inbox')
        result = action.read()[0]
        email_ids = self.env['mail.inbox'].sudo().search([('crm_lead_id','=',self.id)])
        if len(email_ids) != 1:
            result['domain'] = [('crm_lead_id', '=', self.id)]
        elif len(email_ids) == 1:
            result['views'] = [[False, 'form']]
            result['res_id'] = email_ids.id
        result['context'] = {'default_crm_lead_id': self.id, 'default_state': 'inbox'}
        return result

Lead()