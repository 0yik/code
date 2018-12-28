from odoo import fields, models, api

class mail_message(models.Model):

    _inherit = 'mail.message'

    from_incomming_server = fields.Many2one('fetchmail.server', 'Fetch Mail Server ID')

    @api.model
    def create(self, vals):
        if not self._context.get('fetchmail_server_inbox', False) and self._context.get('fetchmail_server_id', False):
            vals['from_incomming_server']  = self._context.get('fetchmail_server_id', False)
        res = super(mail_message, self).create(vals)
        return res