# -*- coding: utf-8 -*-

from odoo import models, fields, api

class helpdesk_ticket(models.Model):
    _name = 'helpdesk.ticket.completed'

    completed_id                = fields.Many2one('helpdesk.ticket',ondelete='set null',string='Completed Id')
    received_date               = fields.Date('Received Date')
