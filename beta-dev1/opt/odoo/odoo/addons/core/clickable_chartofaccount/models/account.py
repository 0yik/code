from odoo import models, fields, api, _

class AccountAccountType(models.Model):
    _inherit = 'account.account.type'

    type = fields.Selection(selection_add=[('view', 'View')])

AccountAccountType()

class Account(models.Model):
    _inherit = 'account.account'

    @api.multi
    def _compute_account_debit_credit_balance(self):
        if self._context.get('date_from'):
            date_from = self._context.get('date_from')
        else:
            date_from = False

        if self._context.get('date_to'):
            date_to = self._context.get('date_to')
        else:
            date_to = False

        if self._context.get('target_move') and self._context.get('target_move') == 'all':
            target_move = ('draft', 'posted')
        else:
            target_move = ('posted',)

        mapping = {
            'balance': "COALESCE(SUM(line.debit),0) - COALESCE(SUM(line.credit), 0) as balance",
            'debit': "COALESCE(SUM(line.debit), 0) as debit",
            'credit': "COALESCE(SUM(line.credit), 0) as credit",
        }

        if self._context.get('target_move') and self._context.get('date_from') and self._context.get('date_to'):
            self._cr.execute("SELECT line.account_id, " +\
                            ', '.join(mapping.values()) +
                            " FROM account_move_line as line, \
                             account_account as account, \
                             account_move AS move \
                             WHERE line.account_id = account.id \
                             AND move.id = line.move_id \
                             AND move.state in %(state)s \
                             AND %(date_from)s <= line.date \
                             AND %(date_to)s >= line.date \
                             GROUP BY line.account_id", {'state': target_move, 'date_from': date_from, 'date_to': date_to})
        elif self._context.get('target_move') and self._context.get('date_from') and not self._context.get('date_to'):
            self._cr.execute("SELECT line.account_id, " +\
                             ', '.join(mapping.values()) +
                            " FROM account_move_line as line, \
                             account_account as account, \
                             account_move AS move \
                             WHERE line.account_id = account.id \
                             AND move.id = line.move_id \
                             AND move.state in %(state)s \
                             AND %(date_from)s <= line.date \
                             GROUP BY line.account_id", {'state': target_move, 'date_from': date_from})
        elif self._context.get('target_move') and not self._context.get('date_from') and self._context.get('date_to'):
            self._cr.execute("SELECT line.account_id, " +\
                            ', '.join(mapping.values()) +
                            " FROM account_move_line as line, \
                             account_account as account, \
                             account_move AS move \
                             WHERE line.account_id = account.id \
                             AND move.id = line.move_id \
                             AND move.state in %(state)s \
                             AND %(date_to)s >= line.date \
                             GROUP BY line.account_id", {'state': target_move, 'date_to': date_to})
        elif self._context.get('target_move') and not self._context.get('date_from') and not self._context.get('date_to'):
            self._cr.execute("SELECT line.account_id, " +\
                            ', '.join(mapping.values()) +
                            " FROM account_move_line as line, \
                             account_account as account, \
                             account_move AS move \
                             WHERE line.account_id = account.id \
                             AND move.id = line.move_id \
                             AND move.state in %(state)s \
                             GROUP BY line.account_id", {'state': target_move})

        for row in self._cr.dictfetchall():
            total_debit = 0.0
            total_credit = 0.0
            total_balance = 0.0
            main_debit = 0.0
            main_credit = 0.0
            main_balance = 0.0
            account = self.env['account.account'].browse(row['account_id'])
            for record in self:
                if record.id == account.id:
                    total_debit += row['debit']
                    total_credit += row['credit']
                    total_balance += row['balance']
                    record.debit = total_debit
                    record.credit = total_credit
                    record.balance = total_balance
                if record.internal_type == 'view' and record.child_account_ids:
                    for line in record.child_account_ids:
                        main_debit += line.debit
                        main_credit += line.credit
                        main_balance += line.balance
                    record.debit = main_debit
                    record.credit = main_credit
                    record.balance = main_balance

    parent_id = fields.Many2one('account.account', string='Parent')
    child_account_ids = fields.One2many('account.account', 'parent_id', string='Child Accounts')
    balance = fields.Monetary(compute='_compute_account_debit_credit_balance', string='Balance')
    debit = fields.Monetary(compute='_compute_account_debit_credit_balance', string='Debit')
    credit = fields.Monetary(compute='_compute_account_debit_credit_balance', string='Credit')

Account()