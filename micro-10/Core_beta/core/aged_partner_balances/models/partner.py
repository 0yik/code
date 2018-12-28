from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_ids = fields.Many2many('res.users', string='Salesperson')

ResPartner()