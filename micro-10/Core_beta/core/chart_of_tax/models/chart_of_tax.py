from odoo import api, fields, models, _

class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    def _sum_amount(self):
        res = {}
        if  self._context.get('date_from'):
            date_from = self._context.get('date_from')
        if  self._context.get('date_to'):
            date_to = self._context.get('date_to')

        if self._context.get('target_move'):
            target_move = self._context.get('target_move')
            if target_move == 'all':
                target_move = ('draft', 'posted')
            else:
                target_move = ('posted',)
        if self._context.get('target_move') and  self._context.get('date_from') and  self._context.get('date_to'):
            self._cr.execute('SELECT line.tax_line_id, ABS(sum(line.debit - line.credit)) \
                FROM account_move_line as line, \
                account_tax as tax, \
                account_move AS move \
                WHERE line.tax_line_id = tax.id \
                AND move.id = line.move_id \
                AND move.state in %(state)s \
                AND %(date_from)s <= line.date \
                AND %(date_to)s >= line.date \
                GROUP BY line.tax_line_id', {'state':target_move, 'date_from':date_from, 'date_to': date_to})
            res = dict(self._cr.fetchall())
        elif self._context.get('target_move') and  self._context.get('date_from') and not self._context.get('date_to'):
            self._cr.execute('SELECT line.tax_line_id, ABS(sum(line.debit - line.credit)) \
                FROM account_move_line as line, \
                account_tax as tax, \
                account_move AS move \
                WHERE line.tax_line_id = tax.id \
                AND move.id = line.move_id \
                AND move.state in %(state)s \
                AND %(date_from)s <= line.date \
                GROUP BY line.tax_line_id', {'state':target_move, 'date_from':date_from})
            res = dict(self._cr.fetchall())
        elif self._context.get('target_move') and not self._context.get('date_from') and  self._context.get('date_to'):
            self._cr.execute('SELECT line.tax_line_id, ABS(sum(line.debit - line.credit)) \
                FROM account_move_line as line, \
                account_tax as tax, \
                account_move AS move \
                WHERE line.tax_line_id = tax.id \
                AND move.id = line.move_id \
                AND move.state in %(state)s \
                AND %(date_to)s >= line.date \
                GROUP BY line.tax_line_id', {'state':target_move, 'date_to': date_to})
            res = dict(self._cr.fetchall())
        elif self._context.get('target_move') and not self._context.get('date_from') and not self._context.get('date_to'):
            self._cr.execute('SELECT line.tax_line_id, ABS(sum(line.debit - line.credit)) \
                FROM account_move_line as line, \
                account_tax as tax, \
                account_move AS move \
                WHERE line.tax_line_id = tax.id \
                AND move.id = line.move_id \
                AND move.state in %(state)s \
                GROUP BY line.tax_line_id', {'state':target_move})
            res = dict(self._cr.fetchall())

        for record in self:
            def _rec_get(record):
                amount = res.get(record.id) or 0.0
                for rec in record.child_ids:
                    amount += _rec_get(rec) * int(rec.sign)
                return amount
            # record.amount = round(_rec_get(record))
            record.amount_total = round(_rec_get(record))

    parent_id = fields.Many2one('account.tax', 'Parent Code', select=True)
    child_ids = fields.One2many('account.tax', 'parent_id', 'Child Codes', copy=True)
    sign = fields.Selection([('1', '+ve'),('-1', '-ve')], string="Sign" , default='1', required=True)
    # amount = fields.Float('Amount', compute='_sum_amount')
    amount_total = fields.Float('Amount', compute='_sum_amount')
