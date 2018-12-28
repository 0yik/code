# -*- coding: utf-8 -*-

from odoo import models, fields, api
from email.utils import parseaddr


class heldpesk_ticket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def message_new(self, msg, custom_values=None):
        res = super(heldpesk_ticket, self).message_new(msg, custom_values)
        helpdesk = self.browse(res)

        # check default department incomming
        if self._context.get('fetchmail_server_id', False):
            server_id = self.env['fetchmail.server'].browse(self._context.get('fetchmail_server_id'))
            if server_id and server_id.id and server_id.helpdesk_team and server_id.helpdesk_team.id:
                helpdesk.team_id = server_id.helpdesk_team.id

        # check Routing for ticket
        domain_team_obj = self.env['routing.helpdesk.team.line']
        domain_user_obj = self.env['routing.res.users.line']

        email_from = msg.get('from')
        domain = parseaddr(email_from)[1].split('@')[1]
        subject = email_from = msg.get('subject', False)

        domain_team_ids = False
        domain_user_ids = False
        team_ids = False
        user_ids = False

        if subject and subject != '':
            # priority to subject
            line_team_ids = domain_team_obj.search([('sale_team_id', '!=', False), ('team_domain', '!=', False)])
            subject_check = line_team_ids.filtered(lambda r: r.subject_check != False).filtered(
                lambda r: subject.startswith(r.subject_check))
            team_ids = subject_check.filtered(lambda r: r.name == domain)
            if len(team_ids) == 0:
                team_ids = subject_check.filtered(lambda r: r.name == False)
            if len(team_ids) == 0:
                team_ids = line_team_ids.filtered(lambda r: r.subject_check == False).filtered(
                    lambda r: r.name == domain)

            line_user_ids = domain_user_obj.search([('user_id', '!=', False), ('user_domain', '!=', False)])
            subject_check = line_user_ids.filtered(lambda r: r.subject_check_user != False).filtered(
                lambda r: subject.startswith(r.subject_check_user))
            user_ids = subject_check.filtered(lambda r: r.name == domain)
            if len(user_ids) == 0:
                user_ids = subject_check.filtered(lambda r: r.name == False)
            if len(user_ids) == 0:
                user_ids = line_user_ids.filtered(lambda r: r.subject_check_user == False).filtered(
                    lambda r: r.name == domain)

        else:
            team_ids = domain_team_obj.search(
                [('name', '=', domain), ('sale_team_id', '!=', False), ('subject_check', '=', False),
                 ('team_domain', '!=', False)])
            user_ids = domain_user_obj.search([('name', '=', domain), ('user_id', '!=', False),
                                               ('subject_check_user', '=', False), ('user_domain', '!=', False)])

        if team_ids and len(team_ids) > 0:
            helpdesk.team_id = team_ids[0].sale_team_id.id
        if user_ids and len(user_ids) > 0:
            helpdesk.user_id = user_ids[0].user_id.id
        return res
