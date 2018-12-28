from odoo import api, fields, models, _

class AccountAnalyticLevel(models.Model):
    _inherit = 'account.analytic.level'
    _order='sequence'

    sequence = fields.Integer('sequence', help="Sequence for the handle.")
    
