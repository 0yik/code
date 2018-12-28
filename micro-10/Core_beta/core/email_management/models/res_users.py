from odoo import models, api, fields

class res_users(models.Model):
    _inherit = "res.users"

    incomming_mail_server = fields.Many2one('fetchmail.server.inbox',string='Incomming Mail Server')
    outgoing_mail_server = fields.Many2one('ir.mail_server.outgoing',string='Outgoing Mail Server')