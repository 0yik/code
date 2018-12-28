from odoo import fields, api, models

class dzh_users(models.Model):
    _inherit = 'res.users'

    re_notification = fields.Boolean()