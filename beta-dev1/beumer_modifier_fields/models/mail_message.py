from odoo import api, fields, models,_
from email.utils import formataddr

class message_inherit(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _get_default_from(self):
        if self.env.user.email:
            return formataddr((self.env.user.name, self.env.user.email))
