from odoo import models, fields

class AccountAssetRevaluation(models.Model):
    _name = 'account.asset.revaluation'

    revaluation_date = fields.Date(string='Revaluation Date')
    revaluation_reason = fields.Char(string="Revaluation Reason")
    new_value = fields.Float(string="New Value")
    old_value = fields.Float(string="Old Value")
    change_value = fields.Float('Change')
    cumulative_value = fields.Float('Cumulative Change')
    asset_id = fields.Many2one('account.asset.asset', string="Assets")
    
    
