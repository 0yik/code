from odoo import models, fields, api
from odoo.exceptions import UserError

class AssetRevalueWizard(models.TransientModel):
    _name = 'asset.revalue.wizard'

    amount = fields.Float('Revalued Amount')
    reason = fields.Char('Reason')
    no_of_depreciation = fields.Integer('Number of Depreciation')
    no_of_month = fields.Integer('Number of Months')

    @api.multi
    def button_confirm(self):
        ctx = self._context if self._context else {}
        if ctx.get('asset_id'):
            asset_obj = self.env['account.asset.asset'].browse(ctx.get('asset_id'))
            if self.amount == asset_obj.value_residual:
                raise UserError("Revalued Amount should not be equal to residual amount")
            if not asset_obj.category_id.journal_id:
                raise UserError("Error!\nJournal not configured in asset category")
            if not asset_obj.category_id.account_asset_id:
                raise UserError("Error!\nAsset account not configured in asset category")
            if not asset_obj.category_id.account_surplus_id:
                raise UserError("Error!\nRevaluation Surplus account not configured in asset category")
            if not asset_obj.category_id.account_loss_id:
                raise UserError("Error!\nRevaluation Loss account not configured in asset category")
            line_list = []
            company_currency = asset_obj.company_id.currency_id
            current_currency = asset_obj.currency_id
            amount = abs(self.amount - asset_obj.value_residual)
            if self.amount > asset_obj.value_residual:
                move_line_1 = {
                    'name': asset_obj.name,
                    'account_id': asset_obj.category_id.account_asset_id.id,
                    'debit': amount,
                    'credit': 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and - 1.0 * amount,
                }
                line_list.append((0, 0, move_line_1))
                move_line_2 = {
                    'name': asset_obj.name,
                    'account_id': asset_obj.category_id.account_surplus_id.id,
                    'credit': amount,
                    'debit': 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and amount,
                }
                line_list.append((0, 0, move_line_2))
            else:
                move_line_1 = {
                    'name': asset_obj.name,
                    'account_id': asset_obj.category_id.account_loss_id.id,
                    'debit': amount,
                    'credit': 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and - 1.0 * amount,
                }
                line_list.append((0, 0, move_line_1))
                move_line_2 = {
                    'name': asset_obj.name,
                    'account_id': asset_obj.category_id.account_asset_id.id,
                    'credit': amount,
                    'debit': 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and amount,
                }
                line_list.append((0, 0, move_line_2))

            move_vals = {
                'ref': asset_obj.name,
                'date': fields.Datetime.now(),
                'journal_id': asset_obj.category_id.journal_id.id,
                'line_ids': line_list,
            }
            move = self.env['account.move'].create(move_vals)
            move.post()
            asset_obj.write({'value': self.amount, 'method_number': self.no_of_depreciation, 'method_period': self.no_of_month})
            asset_obj.compute_depreciation_board()
            return {'type': 'ir.actions.act_window_close'}

AssetRevalueWizard()