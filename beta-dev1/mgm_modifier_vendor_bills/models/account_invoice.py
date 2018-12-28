from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    asset_id = fields.Many2one('account.asset.asset', 'Assets')
