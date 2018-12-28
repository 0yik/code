# coding: utf-8

from odoo import api, fields, models
from odoo import api, fields, models, tools, _

class account_journal(models.Model):
    _inherit = 'account.journal'

    entry_posted =  fields.Boolean('Autopost Created Moves', help='Check this box to automatically post entries of this journal. Note that legally, some entries may be automatically posted when the source document is validated (Invoices), whatever the status of this field.')


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        move = super(AccountMove, self.with_context(check_move_validity=False, partner_id=vals.get('partner_id'))).create(vals)
        journal = self.env['account.journal'].browse(vals['journal_id'])
        if journal.entry_posted:
            move.post()
        return move