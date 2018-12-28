# coding: utf-8

from odoo import api, fields, models

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    # @api.model
    # def create(self, vals):
    #     if vals.get('team_id'):
    #         vals.update(self._onchange_team_get_values(self.env['helpdesk.team'].browse(vals['team_id'])))

    #     # context: no_log, because subtype already handle this
    #     ticket = super(HelpdeskTicket, self.with_context(mail_create_nolog=False)).create(vals)
    #     ticket = 
    #     if ticket.partner_id:
    #     #     ticket.message_subscribe(partner_ids=ticket.partner_id.ids)
    #         ticket._onchange_partner_id()
    #     if ticket.user_id:
    #         ticket.assign_date = ticket.create_date
    #         ticket.assign_hours = 0

    #     return ticket

    @api.multi
    def assign_ticket_to_self(self):
        self.sudo().ensure_one()
        self.sudo().write({'user_id': self.env.user.id})

