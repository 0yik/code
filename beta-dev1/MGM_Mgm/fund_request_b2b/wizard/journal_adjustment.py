from odoo import api, fields, models, _
from datetime import datetime

class journaladjustment(models.TransientModel):
    _name = 'journal.adjustment'

    bank_account_id = fields.Many2one('account.account','Fund Transfer Clearing Account')
    account_journal_id = fields.Many2one('account.journal','Journal')


    @api.multi
    def create_journal_entry(self):
        active_id = self._context.get('active_id')
        fund_transfer_obj = self.env['fund.transfer']
        fund_transfer_rec = fund_transfer_obj.browse(active_id)
        account_move_obj = self.env['account.move']
        line_to_create = []
        line_to_create.append((0, 0, {
                        'name': '/',
                        'debit': 0.0,
                        'credit': fund_transfer_rec.amount_transfer,
                        'account_id': self.bank_account_id.id,
                        'tax_exigible': True,
        }))
        line_to_create.append((0, 0, {
                        'name': '/',
                        'debit': fund_transfer_rec.amount_transfer,
                        'credit': 0.0,
                        'account_id': fund_transfer_rec.bank_account.id,
                        'tax_exigible': True,
        }))
        vals = {}
        fund_obj = self.env['fund.config.settings'].search([])[-1]
        if fund_obj.group_use_journal == 'posted':
            vals.update({
                'journal_id':self.account_journal_id.id,
                'line_ids': line_to_create,
                'state':'posted'
            })
        else:
            vals.update({
                'journal_id':self.account_journal_id.id,
                'line_ids': line_to_create,
                'state':'draft'
            })
        move_id = account_move_obj.create(vals)
        fund_transfer_rec.move_id = move_id.id
        fund_transfer_rec.state = 'posted'


