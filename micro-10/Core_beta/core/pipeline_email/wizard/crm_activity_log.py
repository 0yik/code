from odoo import api, fields, models

class ActivityLog(models.TransientModel):
    _inherit = "crm.activity.log"

    email_from = fields.Char('Email')
    body = fields.Text(default=lambda self: self.env.user.signature)

    @api.multi
    def action_send_email(self):
        ctx = self._context or {}
        self.ensure_one()
        mail_values = {
            'email_from': self.sudo().env.user.partner_id.email,
            'email_to': self.email_from,
            'subject': self.title_action,
            'body': self.body,
            'state': 'inbox',
            'model': 'crm.lead',
            'crm_lead_id': ctx.get('default_lead_id')
        }
        self.env['mail.inbox'].create(mail_values)
        return True


ActivityLog()