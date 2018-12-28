# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError
from datetime import date, datetime

class BankTransaction(models.Model):
    _inherit= 'bank.transaction'

    bank_transaction_line_ids = fields.One2many('bank.transaction.line','bank_transaction_id',string='Bank')

    @api.model
    def create(self,vals):
        total = 0
        if 'bank_transaction_line_ids' in vals:
            for line in vals['bank_transaction_line_ids']:
                total += line[2]['amount_currency']
            if float_compare(total, vals['amount'], 2) == 1:
                raise UserError(
                    _('Total of all Amount Currency cannot be more than Amount.'))

        res = super(BankTransaction, self).create(vals)
        return res

    @api.multi
    def write(self,vals):
        total = 0
        res = super(BankTransaction, self).write(vals)
        for line in self.bank_transaction_line_ids:
            total += line.amount_currency
        if float_compare(total, self.amount, 2) == 1:
            raise UserError(
                _('Total of all Amount Currency cannot be more than Amount.'))

        return res
    
    @api.multi
    def action_post(self):
        line_list = []
        for record in self:
            if record.type == 'out':
                credit_line_vals = {
                    'name': record.reference,
                    'debit': 0.0,
                    'credit': record.amount,
                    'account_id': record.bank_account_id.cash_account.id
                }
                line_list.append((0, 0, credit_line_vals))
                for line in record.bank_transaction_line_ids:
                    debit_line_vals = {
                        'name': record.reference,
                        'debit': line.amount_currency,
                        'credit': 0.0,
                        'account_id': line.bank_account_id.cash_account.id,
                    }
                    line_list.append((0, 0, debit_line_vals))
            else:
                debit_line_vals = {
                    'name': record.reference,
                    'debit': record.amount,
                    'credit': 0.0,
                    'account_id': record.bank_account_id.cash_account.id
                }
                line_list.append((0, 0, debit_line_vals))
                for line in record.bank_transaction_line_ids:
                    credit_line_vals = {
                        'name': record.reference,
                        'debit': 0.0,
                        'credit': line.amount_currency,
                        'account_id': line.bank_account_id.cash_account.id,
                    }
                    line_list.append((0, 0, credit_line_vals))
            move = self.env['account.move'].create({
                'name': '/',
                'journal_id': record.journal_id.id,
                'date': record.date or date.today(),
                'line_ids': line_list,
                'ref': record.name
            })
            move.post()
            self.write({'state': 'posted',
                        'move_id': move.id
                        })
        return True

class BankTransactionLine(models.Model):
    _name = 'bank.transaction.line'

    branch_id           = fields.Many2one('res.branch', string='Branch')
    bank_account_id     = fields.Many2one('account.journal', string='Bank')
    amount_currency     = fields.Float(string='Amount Currency')
    bank_transaction_id = fields.Many2one('bank.transaction', string='Bank Transaction')

