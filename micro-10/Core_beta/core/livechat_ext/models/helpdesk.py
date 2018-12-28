# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from odoo import api, fields, models, _

class MailChannel(models.Model):
    _inherit = 'mail.channel'

    # ------------------------------------------------------
    #  Commands
    # ------------------------------------------------------

    def _define_command_helpdesk(self):
        return {'help': _("Create a new helpdesk ticket")}

    def _execute_command_helpdesk(self, **kwargs):
        key = kwargs.get('body').split()
        partner = self.env.user.partner_id
        msg = _('Something is missing or wrong in command')
        channel_partners = self.env['mail.channel.partner'].search([('partner_id', '!=', partner.id), ('channel_id', '=', self.id)], limit=1)
        if key[0].lower() == '/helpdesk':
            if len(key) == 1:
                if self.channel_type == 'channel':
                    msg = _("You are in channel <b>#%s</b>.") % self.name
                    if self.public == 'private':
                        msg += _(" This channel is private. People must be invited to join it.")
                else:
                    msg = _("You are in a private conversation with <b>@%s</b>.") % channel_partners.partner_id.name
                msg += _("""<br><br>
                    You can create a new ticket by typing <b>/helpdesk "ticket title"</b>.<br>
                    You can search ticket by typing <b>/helpdesk_search "Keywords1 Keywords2 etc"</b><br>
                    """)
            else:
                list_value = key[1:]
                description = ''
                for message in self.channel_message_ids.sorted(key=lambda r: r.id):
                    name = message.author_id.name or 'Anonymous'
                    description += '%s: ' % name + '%s\n' % re.sub('<[^>]*>', '', message.body)
                team = self.env['helpdesk.team'].search([('member_ids', 'in', self._uid)], order='sequence', limit=1)
                team_id = team.id if team else False
                customer_ids = []
                partner_id = False
                if self.anonymous_email:
                    customer_id = self.env['res.partner'].search([('email','=',self.anonymous_email)],  limit=1)
                if customer_id:
                    partner_id = customer_id.id
                    email = customer_id.email if customer_id.email else False
                else:
                    partner_id = channel_partners.partner_id.id
                    email = self.anonymous_email if self.anonymous_email else False
                helpdesk_ticket = self.env['helpdesk.ticket'].create({
                    'name': ' '.join(list_value),
                    'user_id': self.env.user.id,
                    'description': description,
                    'partner_id': partner_id,
                    'partner_email': email,
                    'team_id': team_id,
                })
                link_ticket = '<a href="#" data-oe-id='+str(helpdesk_ticket.id)+' data-oe-model="helpdesk.ticket">'+helpdesk_ticket.name+'</a>'
                msg = _("Created a new ticket and request: %s") % link_ticket
        return self._send_transient_message(partner, msg)
