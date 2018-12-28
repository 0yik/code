from odoo import api, fields, models, _, tools
import datetime

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    asset_history_ids = fields.One2many('account.asset.history', 'asset_id', string='Movement History')

    @api.multi
    def write(self, vals):
        previous_user = self.owner_id.id
        res = super(AccountAssetAsset, self).write(vals)
        if vals.get('owner_id'):
            vals = {
                'asset_id': self.id,
                'asset_category_id': self.category_id.id,
                'current_user_id': vals.get('owner_id'),
                'previous_user_id': previous_user,
                'date_transferred': datetime.date.today()
            }
            self.env['account.asset.history'].create(vals)
        return res

