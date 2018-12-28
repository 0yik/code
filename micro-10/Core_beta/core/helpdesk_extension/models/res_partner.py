# coding: utf-8

from odoo import api, fields, models


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    tickets_count = fields.Integer("Tickets", compute='_compute_tickets_count')

    @api.multi
    def _compute_tickets_count(self):
        for partner in self:
            partner.tickets_count = self.env['helpdesk.ticket'].search_count([('partner_id', '=', partner.id)])

    @api.multi
    def _notify(self, message, force_send=False, send_after_commit=True, user_signature=True):
        server_sudo = self.env['fetchmail.server'].sudo()
        server_email = server_sudo.search([]).mapped('user')
        record = self.sudo().search([('email','not in',server_email),('id', 'in', self.ids)])

        res = super(res_partner, record)._notify(message, force_send=force_send, send_after_commit=send_after_commit,
                                               user_signature=user_signature)
        return res
