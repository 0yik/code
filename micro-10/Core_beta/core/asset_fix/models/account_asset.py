from odoo import models, fields, api

class AccountDiscountSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    asset_account = fields.Many2one('account.account', string="Gain/Loss on Asset Disposal")

    @api.multi
    def set_asset_account(self):
        return self.env['ir.values'].sudo().set_default( 'account.config.settings', 'asset_account', self.asset_account.id)

class account_asset_asset(models.Model):
    _inherit = 'account.asset.asset'

    state = fields.Selection(selection_add=[('disposed', 'Disposed')])
    dispose_move_id = fields.Many2one('account.move', string='Disposal Move', copy=False)
    owner_id = fields.Many2one('res.users', 'Owner')
    asset_location_id = fields.Many2one('account.asset.location', string="Asset Location")

    @api.multi
    @api.depends('depreciation_line_ids.move_id', 'dispose_move_id')
    def _entry_count(self):
        for asset in self:
            res = self.env['account.asset.depreciation.line'].search_count([('asset_id', '=', asset.id), ('move_id', '!=', False)])
            if asset.dispose_move_id:
                res += 1
            asset.entry_count = res or 0

    @api.multi
    def button_revalue_asset(self):
        return {
            'name': 'Revalue Asset Wizard',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asset.revalue.wizard',
            'target': 'new',
            'context': {'asset_id': self.id},
        }

    @api.multi
    def set_to_close(self):
        return {
            'name': 'Sell / Dispose Asset Wizard',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'journal.creation.wizard',
            'target': 'new',
            'context': {'asset_id': self.id},
        }

    @api.multi
    def open_entries(self):
        move_ids = []
        for asset in self:
            for depreciation_line in asset.depreciation_line_ids:
                if depreciation_line.move_id:
                    move_ids.append(depreciation_line.move_id.id)
            if asset.dispose_move_id:
                move_ids.append(asset.dispose_move_id.id)
        return {
            'name': 'Journal Entries',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids)],
        }

account_asset_asset()

class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    account_surplus_id = fields.Many2one('account.account', string='Revaluation Surplus')
    account_loss_id = fields.Many2one('account.account', string='Revaluation Loss')
    gain_asset_disposal = fields.Many2one('account.account', string='Gain of Asset Disposal')
    loss_asset_disposal = fields.Many2one('account.account', string='Loss of Asset Disposal')

AccountAssetCategory()
