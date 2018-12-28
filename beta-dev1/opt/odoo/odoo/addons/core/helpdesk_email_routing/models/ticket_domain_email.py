# -*- coding: utf-8 -*-

from odoo import models, fields, api

class helpdesk_email_routing(models.Model):
    _name = 'helpdesk.email.routing'


    name = fields.Char('Name')
    # domain_email_for_all = fields.Many2one('res.users', string='Domain Email')
    saleteam_domain_ids = fields.One2many('routing.helpdesk.team.line', 'team_domain', 'Helpdesk Team Routing')
    saleman_domain = fields.One2many('routing.res.users.line', 'user_domain', 'User Routing')


class crm_case_section_line(models.Model):
    _name = 'routing.helpdesk.team.line'

    name = fields.Char('Domain')
    subject_check = fields.Char('Subject')
    team_domain = fields.Many2one('helpdesk.email.routing', 'Domain Configuration')
    sale_team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team')

class res_users_line(models.Model):
    _name = 'routing.res.users.line'

    name = fields.Char('Domain')
    subject_check_user = fields.Char('Subject')
    user_domain = fields.Many2one('helpdesk.email.routing', 'Domain Configuration')
    user_id = fields.Many2many('res.users', string='Assignee')