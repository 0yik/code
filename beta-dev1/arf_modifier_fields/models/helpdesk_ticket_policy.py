# -*- coding: utf-8 -*-

from odoo import models, fields, api


class helpdesk_ticket(models.Model):
    _name = 'helpdesk.ticket.policy'

    policy_id = fields.Many2one('helpdesk.ticket', ondelete='set null', string='Cover Id')
    policy = fields.Char('Policy')
    date = fields.Date('Date')
    status = fields.Selection([], 'Status')