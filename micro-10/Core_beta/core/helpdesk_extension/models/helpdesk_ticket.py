# coding: utf-8

import re
from odoo import api, fields, models

class helpdesk_ticket(models.Model):
    _inherit = 'helpdesk.ticket'

    message_id = fields.Char('Message Id')
    recipient = fields.Char('Recipient')

    @api.model
    def message_new(self, msg, custom_values=None):
        if custom_values is None:
            custom_values = {}

        if msg.get('message_id', False):
            custom_values.update({'message_id' : msg.get('message_id')})

        if self._context.get('fetchmail_server_id', False) and msg.get('from', False):
            mail_server = self.env['fetchmail.server'].browse(self.env.context.get('fetchmail_server_id'))
            custom_values.update({
                'description': msg.get('from'),
                'recipient': mail_server.user,
            })
            if mail_server and mail_server.id and mail_server.helpdesk_team and mail_server.helpdesk_team.id:
                custom_values.update({
                    'team_id': mail_server.helpdesk_team.id,
                })
        result = super(helpdesk_ticket, self.with_context({'send_track_template': True})).message_new(msg, custom_values)
        return result

    @api.multi
    def message_update(self, msg_dict, update_vals=None):
        if update_vals is None:
            update_vals = {}
        for record in self:
            stage_id = self.env['helpdesk.stage'].search([
                ('team_ids', 'in', record.team_id.id),
            ], limit=1).id
            update_vals.update({'stage_id': stage_id})
        result = super(helpdesk_ticket, self.with_context({'send_track_template': False})).message_update(msg_dict, update_vals)
        return result

    @api.multi
    def _track_template(self, tracking):
        res = super(helpdesk_ticket, self)._track_template(tracking)
        if 'stage_id' in res:
            if not self.env.context.get('send_track_template', False):
                del (res['stage_id'])
        return res
