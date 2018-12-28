# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class helpdesk_ticket(models.Model):
    _name = 'helpdesk.ticket.email'

    ticket_id = fields.Many2one('helpdesk.ticket', ondelete='set null', string='Email Id')
    email_id  = fields.Many2one('mail.message')
    subject   = fields.Char('Subject')
    body      = fields.Text("Body")
    date      = fields.Date('Date')
    status    = fields.Char('Status')

    @api.onchange('email_id')
    def onchange_email_id(self):
        if self.email_id:
            self.subject = self.email_id.subject or ''
            self['body'] = self.email_id.body
            self.date = datetime.strptime(self.email_id.date, '%Y-%m-%d %H:%M:%S').date()


    @api.multi
    def action_reply(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.inbox',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'email_to':True,
                'default_email_to': self.email_id.email_from,
                'default_model': 'helpdesk.ticket',
                'default_res_id': self.ticket_id.id,
		'body_html': self.body,
                'subject': self.subject
            }

        }

    @api.multi
    # def action_forward(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'mail.inbox',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'email_to': True,
    #             'default_model': 'helpdesk.ticket',
    #             'default_res_id': self.ticket_id.id,
    #         }

    def action_forward(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.inbox',
            'view_mode': 'form',
            'target': 'new',
            'views': [[False, "form"]],
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}},
            'context': {
                'email_to': True,
                'default_model': 'helpdesk.ticket',
                'default_res_id': self.ticket_id.id,
                'body_html': self.body,
                'subject': self.subject
            },
        }
