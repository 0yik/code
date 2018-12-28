from odoo import models, api

class JournalCreationWizard(models.TransientModel):
    _inherit = 'journal.creation.wizard'

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
            if ctx.get('asset_master_id'):
                asset_master_obj = self.env['asset.master'].browse(ctx.get('asset_master_id'))
                asset_master_obj.write({'state': 'dispose'})

            return {
                'name': 'Disposal Moves',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id','in',move_ids)],
            }

JournalCreationWizard()