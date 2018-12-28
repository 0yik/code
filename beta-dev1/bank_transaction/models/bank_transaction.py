# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError
from datetime import date, datetime

class BankTransaction(models.Model):
    _name = 'bank.transaction'

    name = fields.Char()
    type       = fields.Selection([('in','Transfer In'),('out','Transfer Out')], string='Type',required=True)
    journal_id = fields.Many2one('account.journal', string='Journal')
    date       = fields.Date(string='Date')
    reference  = fields.Char(string='Reference')
    bank_account_id = fields.Many2one('account.journal', string='Bank')
    amount     = fields.Float(string='Amount')
    state = fields.Selection([
        ('unposted', 'Unposted'),
        ('posted', 'Posted')
    ], string='Status', default='unposted', copy=False, index=True, readonly=True, help="Status of the Bank Statement.")
    bank_transaction_line_in_ids = fields.One2many('bank.transaction.line.in','bank_transaction_id',string='Bank')
    bank_transaction_line_out_ids = fields.One2many('bank.transaction.line.out','bank_transaction_id',string='Bank')
    move_id = fields.Many2one('account.move')

    @api.model
    def create(self,vals):
        total = 0
        if 'bank_transaction_line_in_ids' in vals:
            for line in vals['bank_transaction_line_in_ids']:
                total += line[2]['amount_currency']
        if 'bank_transaction_line_out_ids' in vals:
            for line in vals['bank_transaction_line_out_ids']:
                total += line[2]['amount_currency']
        if float_compare(total, vals['amount'], 2) == 1:
            raise UserError(
                _('Total of all Amount Currency cannot be more than Amount.'))
        if vals['type'] == 'in':
            name = self.env['ir.sequence'].get('bank.seq.in')
        else:
            name = self.env['ir.sequence'].get('bank.seq.out')
        vals.update({
            'name' : name
        })
        res = super(BankTransaction, self).create(vals)
        return res

    @api.multi
    def write(self,vals):
        total = 0
        res = super(BankTransaction, self).write(vals)
        for line in self.bank_transaction_line_in_ids:
            total += line.amount_currency
        for line in self.bank_transaction_line_out_ids:
            total += line.amount_currency
        if float_compare(total, self.amount, 2) == 1:
            raise UserError(
                _('Total of all Amount Currency cannot be more than Amount.'))

        return res
    
    @api.multi
    def action_post(self):
        line_list = []
        for record in self:
            credit_line_vals = {
                'name': record.reference or '/',
                'credit': record.amount,
                'debit': 0.0,
                'account_id': record.bank_account_id.cash_account.id
            }
            line_list.append((0, 0, credit_line_vals))
            if record.type == 'out':
                for line in record.bank_transaction_line_out_ids:
                    debit_line_vals = {
                        'name': record.reference or '/',
                        'debit': line.amount_currency,
                        'credit': 0.0,
                        'account_id': line.master_expense_id.account_id.id,
                    }
                    line_list.append((0, 0, debit_line_vals))
            else:
                for line in record.bank_transaction_line_in_ids:
                    debit_line_vals = {
                        'name': record.reference or '/',
                        'debit': line.amount_currency,
                        'credit': 0.0,
                        'account_id': line.account_id.id,
                    }
                    line_list.append((0, 0, debit_line_vals))
            move = self.env['account.move'].create({
                'name': '/',
                'journal_id': record.journal_id.id,
                'date': record.date or date.today(),
                'line_ids': line_list,
                'ref': record.name
            })
            move.post()
            self.write({'state': 'posted',
                        'move_id' : move.id
                        })
        return True


class BankTransactionLineIn(models.Model):
    _name = 'bank.transaction.line.in'

    account_id     = fields.Many2one('account.account', string='Account')
    amount_currency     = fields.Float(string='Amount Currency')
    bank_transaction_id = fields.Many2one('bank.transaction', string='Bank Transaction')

class BankTransactionLineOut(models.Model):
    _name = 'bank.transaction.line.out'

    master_expense_id           = fields.Many2one('master.expense', string='Expense')
    description     = fields.Text(related='master_expense_id.description')
    amount_currency     = fields.Float(string='Amount Currency')
    bank_transaction_id = fields.Many2one('bank.transaction', string='Bank Transaction')

class MasterExpense(models.Model):
    _name = 'master.expense'

    name           = fields.Char('Expense Name', required=True)
    description     = fields.Text('Description')
    account_id = fields.Many2one('account.account', string='Account',required=True)
