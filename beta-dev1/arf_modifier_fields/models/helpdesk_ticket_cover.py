# -*- coding: utf-8 -*-

from odoo import models, fields, api


class helpdesk_ticket(models.Model):
    _name = 'helpdesk.ticket.cover'


    cover_id = fields.Many2one('helpdesk.ticket', ondelete='set null', string='Cover Id')
    cover_note = fields.Char('Cover Note')
    date = fields.Date('Date')
    status = fields.Selection([], 'Status')