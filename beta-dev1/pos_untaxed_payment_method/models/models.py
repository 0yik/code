from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    usage_tax = fields.Selection([('taxed', 'Taxed Amount'),('untaxed', 'Untaxed Amount')], string='Usage', default='taxed')


