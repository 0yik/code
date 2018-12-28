# -*- coding: utf-8 -*-

from odoo import models, fields, api

class helpdesk_ticket(models.Model):
    _name = 'helpdesk.ticket.renewal'

    renewal_id = fields.Many2one('helpdesk.ticket', ondelete='set null', string='Renewal Id')
    renewal_notice   = fields.Char('Renewal Notice')
    date      = fields.Date('Date')
    status    = fields.Selection([], 'Status')
