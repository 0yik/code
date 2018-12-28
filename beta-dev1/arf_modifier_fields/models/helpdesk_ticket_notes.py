# -*- coding: utf-8 -*-

from odoo import models, fields, api


class helpdesk_ticket(models.Model):
    _name = 'helpdesk.ticket.notes'


    notes_id       = fields.Many2one('helpdesk.ticket', ondelete='set null', string='Note Id')
    nature         = fields.Char('Nature of the Call')
    description_id = fields.Text('Description')
    user_id        = fields.Many2one('res.users', 'User', default=lambda self: self.env.uid)
    date           = fields.Date('Date', default=lambda self: fields.date.today())

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = ''
            if record.nature:
                name = record.nature 
            result.append((record.id, name))
        return result