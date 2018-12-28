from odoo import api, fields, models, _, tools

class AccountAssetHistory(models.Model):
    _name = 'account.asset.history'

    asset_id = fields.Many2one('account.asset.asset', 'Asset')
    request_id = fields.Many2one('account.asset.request', 'Request')
    asset_category_id = fields.Many2one('account.asset.category', 'Asset Category')
    current_user_id = fields.Many2one('res.users', 'Current User')
    previous_user_id = fields.Many2one('res.users', 'Previous User')
    date_transferred = fields.Date('Date Transferred')
    previous_location_id = fields.Many2one('stock.location','Previous Location')
    current_location_id = fields.Many2one('stock.location','Current Location')
