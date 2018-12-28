from odoo import models, fields, api

class ResBranch(models.Model):
    _inherit = 'res.branch'

    tax_id = fields.Many2one('account.tax', string='Tax')

