from odoo import api, fields, models, tools,exceptions, _

class journal_creation_wizard(models.TransientModel):
    _name = 'journal.creation.wizard'
    _description = 'Journal Creation'

    sold_to = fields.Char('Sold To')
    sale_price = fields.Float('Sale Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    journal_id = fields.Many2one('account.journal', string='Payment Method', domain=[('type', 'in', ('bank', 'cash'))])

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id.id

    @api.multi
    def action_create_journal(self):
        ctx = self._context if self._context else {}
        move_ids = []
        if ctx.get('asset_id'):
            asset_obj = self.env['account.asset.asset'].browse(ctx.get('asset_id'))
            # Existing journal entries
            for line in asset_obj.depreciation_line_ids:
                if line.move_id:
                    move_ids.append(line.move_id.id)
            # Create disposal move
            if asset_obj.value_residual:
                dispose_move_id = self.create_dispose_journal_entry()
            else:
                dispose_move_id = self.create_final_journal_entry()
            asset_obj.dispose_move_id = dispose_move_id
            move_ids.append(dispose_move_id)

            for move_id in move_ids:
                move = self.env['account.move'].browse(move_id)
                move.post()

            asset_obj.write({'state': 'disposed'})

            return {
                'name': 'Disposal Moves',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id','in',move_ids)],
            }

    @api.multi
    def create_dispose_journal_entry(self):
        move_id = False
        ctx = self._context if self._context else {}
        if ctx.get('asset_id'):
            line_list = []
            asset_obj = self.env['account.asset.asset'].browse(ctx.get('asset_id'))
            depreciation_date = fields.Date.context_today(self)
            company_currency = asset_obj.company_id.currency_id
            current_currency = asset_obj.currency_id
            asset_name = asset_obj.name + ' - Disposal to ' + self.sold_to

            gain_or_loss_account_id = self.env['ir.values'].get_default('account.config.settings', 'asset_account')
            if not gain_or_loss_account_id:
                gain_or_loss_account_id = self.env['account.account'].search(
                    [('name', '=', 'Gain/loss on sale of fixed assets or investments')], limit=1)
                if not gain_or_loss_account_id:
                    raise exceptions.Warning(_(
                        'Need a account have code is "301002" or name is "Gain/loss on sale of fixed assets or investments"!'))

            # Calculating depreciated amount
            depreciated_amount = asset_obj.value - asset_obj.value_residual
            # Calculating gain/loss amount
            gain_or_loss_amount = self.sale_price - asset_obj.value_residual

            # Depreciation line
            if depreciated_amount > 0:
                move_line_1 = {
                    'name': asset_name,
                    'account_id': asset_obj.category_id.account_depreciation_id.id,
                    'debit': depreciated_amount,
                    'credit': 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and - 1.0 * depreciated_amount,
                }
                line_list.append((0, 0, move_line_1))
            # Payment method line
            if self.sale_price > 0:
                move_line_2 = {
                    'name': asset_name,
                    'account_id': self.journal_id.default_debit_account_id.id,
                    'debit': self.sale_price,
                    'credit': 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and - 1.0 * self.sale_price,
                }
                line_list.append((0, 0, move_line_2))
            # Asset value line
            if asset_obj.value > 0:
                move_line_3 = {
                    'name': asset_name,
                    'account_id': asset_obj.category_id.account_asset_id.id,
                    'credit': asset_obj.value,
                    'debit': 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and asset_obj.value,
                }
                line_list.append((0, 0, move_line_3))
            # Gain / loss value line
#             if gain_or_loss_amount:
#                 move_line_4 = {
#                     'name': asset_name,
#                     'account_id': gain_or_loss_account_id.id,
#                     'credit': gain_or_loss_amount if gain_or_loss_amount > 0 else 0.0,
#                     'debit': abs(gain_or_loss_amount) if gain_or_loss_amount < 0 else 0.0,
#                     'journal_id': asset_obj.category_id.journal_id.id,
#                     'partner_id': asset_obj.partner_id.id,
#                     'analytic_account_id': False,
#                     'currency_id': company_currency != current_currency and current_currency.id or False,
#                     'amount_currency': company_currency != current_currency and abs(gain_or_loss_amount),
#                 }
#                 line_list.append((0, 0, move_line_4))
                
            if gain_or_loss_amount > 0.0 and gain_or_loss_amount != 0.0:
                move_line_4 = {
                    'name': asset_name,
                    'account_id': asset_obj.category_id.gain_asset_disposal.id, #gain_or_loss_account_id.id,
                    'credit': gain_or_loss_amount if gain_or_loss_amount > 0 else 0.0,
                    'debit': abs(gain_or_loss_amount) if gain_or_loss_amount < 0 else 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and abs(gain_or_loss_amount),
                }
                line_list.append((0, 0, move_line_4))
            if gain_or_loss_amount < 0.0 and gain_or_loss_amount != 0.0:
                move_line_4 = {
                    'name': asset_name,
                    'account_id': asset_obj.category_id.loss_asset_disposal.id, #gain_or_loss_account_id.id,
                    'credit': gain_or_loss_amount if gain_or_loss_amount > 0 else 0.0,
                    'debit': abs(gain_or_loss_amount) if gain_or_loss_amount < 0 else 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and abs(gain_or_loss_amount),
                }
                line_list.append((0, 0, move_line_4))

            if line_list:
                move_vals = {
                    'ref': asset_name,
                    'date': depreciation_date,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'line_ids': line_list,
                }
                move = self.env['account.move'].create(move_vals)
                move_id = move.id

        return move_id

    @api.multi
    def create_final_journal_entry(self):
        move_id = False
        ctx = self._context if self._context else {}
        if ctx.get('asset_id'):
            line_list = []
            asset_obj = self.env['account.asset.asset'].browse(ctx.get('asset_id'))
            depreciation_date = fields.Date.context_today(self)
            company_currency = asset_obj.company_id.currency_id
            current_currency = asset_obj.currency_id
            asset_name = asset_obj.name + ' - Disposal to ' + self.sold_to
            depreciated_amount = asset_obj.value - asset_obj.value_residual

            # Depreciation line
            if depreciated_amount > 0:
                move_line_1 = {
                    'name': asset_name,
                    'account_id': asset_obj.category_id.account_depreciation_id.id,
                    'debit': depreciated_amount,
                    'credit': 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and - 1.0 * depreciated_amount,
                }
                line_list.append((0, 0, move_line_1))
            # Asset value line
            if asset_obj.value > 0:
                move_line_3 = {
                    'name': asset_name,
                    'account_id': asset_obj.category_id.account_asset_id.id,
                    'credit': asset_obj.value,
                    'debit': 0.0,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'partner_id': asset_obj.partner_id.id,
                    'analytic_account_id': False,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and asset_obj.value,
                }
                line_list.append((0, 0, move_line_3))

            if line_list:
                move_vals = {
                    'ref': asset_name,
                    'date': depreciation_date,
                    'journal_id': asset_obj.category_id.journal_id.id,
                    'line_ids': line_list,
                }
                move = self.env['account.move'].create(move_vals)
                move_id = move.id

        return move_id

journal_creation_wizard()