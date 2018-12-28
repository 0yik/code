from odoo import fields, models, api

class hr_expense(models.Model):
    _inherit = 'hr.expense'

    text_reference      = fields.Text('Reference')
    analytic_distribution = fields.Many2one('account.analytic.distribution',string="Analytic Distribution")
    exchange_rate       = fields.Char('Exchange Rate')