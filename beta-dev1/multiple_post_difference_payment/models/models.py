# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"
#
#     _sql_constraints = [
#         ('credit_debit1', 'Check(1=1)', 'Wrong credit or debit value in accounting entry !'),
#         ('credit_debit2', 'Check(1=1)', 'Wrong credit or debit value in accounting entry !'),
#     ]
#
# class AccountMove(models.Model):
#     _inherit = "account.move"
#
#     @api.multi
#     def assert_balanced(self):
#         if not self.ids:
#             return True
#         prec = self.env['decimal.precision'].precision_get('Account')
#
#         self._cr.execute("""\
#                 SELECT      move_id
#                 FROM        account_move_line
#                 WHERE       move_id in %s
#                 GROUP BY    move_id
#                 HAVING      abs(sum(debit) - sum(credit)) > %s
#                 """, (tuple(self.ids), 10 ** (-max(5, prec))))
#         # if len(self._cr.fetchall()) != 0:
#         #     raise UserError(_("Cannot create unbalanced journal entry."))
#         return True

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        if rec and 'amount' in rec and rec.get('amount'):
            rec['amount_default'] = rec['amount']
        return rec

    multiple_post_line = fields.Integer('multiple post line',default=0)
    amount_default = fields.Float('Amount Default')

    writeoff_account_id_1 = fields.Many2one('account.account', string="Difference Account",
                                            domain=[('deprecated', '=', False)], copy=False)
    amount_1 = fields.Monetary(string='Payment Amount', required=True)

    writeoff_account_id_2 = fields.Many2one('account.account', string="Difference Account",
                                            domain=[('deprecated', '=', False)], copy=False)
    amount_2 = fields.Monetary(string='Payment Amount', required=True)

    writeoff_account_id_3 = fields.Many2one('account.account', string="Difference Account",
                                            domain=[('deprecated', '=', False)], copy=False)
    amount_3 = fields.Monetary(string='Payment Amount', required=True)

    writeoff_account_id_4 = fields.Many2one('account.account', string="Difference Account",
                                            domain=[('deprecated', '=', False)], copy=False)
    amount_4 = fields.Monetary(string='Payment Amount', required=True)

    writeoff_account_id_5 = fields.Many2one('account.account', string="Difference Account",
                                            domain=[('deprecated', '=', False)], copy=False)
    amount_5 = fields.Monetary(string='Payment Amount', required=True)

    # def post(self):
    #     # if self.amount and self.amount_default and self.amount_default < self.amount:
    #     # if self.payment_difference < 0:
    #     #     raise ValidationError(_("The total amount that will be posted should not be more than payment amount."))
    #
    #     # if self.amount_default < self.amount:
    #     #     self.payment_difference = self._compute_total_invoices_amount() - amount1
    #
    #     # if self.payment_difference != 0:
    #     #     raise ValidationError(_("The total amount that will be posted should equal to the payment difference."))
    #
    #     if self.payment_difference_handling == 'reconcile':
    #         amount = self.amount_default + self.amount_1 + self.amount_2 + self.amount_3 + self.amount_4 + self.amount_5
    #         amount1 = self.amount_1 + self.amount_2 + self.amount_3 + self.amount_4 + self.amount_5
    #         if self.amount != amount and self.amount_default < self.amount:
    #             raise ValidationError(_("The total amount that will be posted should equal to the payment amount."))
    #         elif amount1 != self.payment_difference and self.amount_default > self.amount:
    #             raise ValidationError(_("The total amount that will be posted should equal to the payment difference."))
    #
    #         # 1
    #         self.writeoff_account_id = self.writeoff_account_id_1
    #         # if self.amount_default < self.amount:
    #         #     self.amount = self.amount_1
    #         if self.multiple_post_line == 0:
    #             res = super(AccountPayment, self).post()
    #             return res
    #         else:
    #             amount = self.amount_1 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
    #             if self.amount_default < self.amount:
    #                 amount *= -1
    #             move = self._create_payment_entry_with_account(amount,self.writeoff_account_id)
    #         # 2
    #         self.writeoff_account_id = self.writeoff_account_id_2
    #         # if self.amount_default < self.amount:
    #         #     self.amount = self.amount_2
    #         if self.multiple_post_line == 1:
    #             res = super(AccountPayment, self).post()
    #             if self.amount_default < self.amount:
    #                 last_move = self.env['account.move'].sudo().search([('ref', '=', self.communication)], limit=1, order='id desc')
    #                 for one_move_line in last_move.line_ids:
    #                     if one_move_line.account_id == self.writeoff_account_id:
    #                         # one_move_line.debit = self.amount_2
    #                         self._cr.execute(
    #                             'UPDATE account_move_line SET credit = %s ' 'WHERE id = %s',
    #                             (str(self.amount_2), one_move_line.id))
    #                         self._cr.commit()
    #             return res
    #         else:
    #             amount = self.amount_2 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
    #             if self.amount_default < self.amount:
    #                 amount *= -1
    #             move = self._create_payment_entry_with_account(amount,self.writeoff_account_id)
    #         # 3
    #         self.writeoff_account_id = self.writeoff_account_id_3
    #         # if self.amount_default < self.amount:
    #         #     self.amount = self.amount_3
    #         if self.multiple_post_line == 2:
    #             res = super(AccountPayment, self).post()
    #             if self.amount_default < self.amount:
    #                 last_move = self.env['account.move'].sudo().search([('ref', '=', self.communication)], limit=1, order='id desc')
    #                 for one_move_line in last_move.line_ids:
    #                     if one_move_line.account_id == self.writeoff_account_id:
    #                         # one_move_line.debit = self.amount_3
    #                         self._cr.execute(
    #                             'UPDATE account_move_line SET credit = %s ' 'WHERE id = %s',
    #                             (str(self.amount_3), one_move_line.id))
    #                         self._cr.commit()
    #             return res
    #         else:
    #             amount = self.amount_3 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
    #             if self.amount_default < self.amount:
    #                 amount *= -1
    #             move = self._create_payment_entry_with_account(amount, self.writeoff_account_id)
    #
    #         # 4
    #         self.writeoff_account_id = self.writeoff_account_id_4
    #         # if self.amount_default < self.amount:
    #         #     self.amount = self.amount_4
    #         if self.multiple_post_line == 3:
    #             res = super(AccountPayment, self).post()
    #             if self.amount_default < self.amount:
    #                 last_move = self.env['account.move'].sudo().search([('ref', '=', self.communication)], limit=1, order='id desc')
    #                 for one_move_line in last_move.line_ids:
    #                     if one_move_line.account_id == self.writeoff_account_id:
    #                         # one_move_line.debit = self.amount_4
    #                         self._cr.execute(
    #                             'UPDATE account_move_line SET credit = %s ' 'WHERE id = %s',
    #                             (str(self.amount_4), one_move_line.id))
    #                         self._cr.commit()
    #             return res
    #
    #         # 5
    #         self.writeoff_account_id = self.writeoff_account_id_5
    #         # if self.amount_default < self.amount:
    #         #     self.amount = self.amount_5
    #         if self.multiple_post_line == 4:
    #             res = super(AccountPayment, self).post()
    #             if self.amount_default < self.amount:
    #                 last_move = self.env['account.move'].sudo().search([('ref', '=', self.communication)], limit=1, order='id desc')
    #                 for one_move_line in last_move.line_ids:
    #                     if one_move_line.account_id == self.writeoff_account_id:
    #                         # one_move_line.debit = self.amount_5
    #                         self._cr.execute(
    #                             'UPDATE account_move_line SET credit = %s ' 'WHERE id = %s',
    #                             (str(self.amount_5), one_move_line.id))
    #                         self._cr.commit()
    #             return res
    #         self.multiple_post_line = 0
    #
    #     else:
    #         res = super(AccountPayment, self).post()
    #         return res
    #
    # @api.multi
    # def show_new_post_payment(self):
    #     if self.multiple_post_line != 4:
    #         self.multiple_post_line += 1
    #     return {
    #         "type": "ir.actions.do_nothing",
    #     }
    #
    # def _create_payment_entry_with_account(self, amount, account):
    #     """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
    #         Return the journal entry.
    #     """
    #     aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
    #     invoice_currency = False
    #     if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
    #         #if all the invoices selected share the same currency, record the paiement in that currency too
    #         invoice_currency = self.invoice_ids[0].currency_id
    #     debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)
    #
    #     move = self.env['account.move'].create(self._get_move_vals())
    #
    #     #Write line corresponding to invoice payment
    #     counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
    #     counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
    #     counterpart_aml_dict.update({'currency_id': currency_id})
    #     counterpart_aml = aml_obj.create(counterpart_aml_dict)
    #
    #     self.invoice_ids.register_payment(counterpart_aml)
    #
    #     #Write counterpart lines
    #     if not self.currency_id != self.company_id.currency_id:
    #         amount_currency = 0
    #     liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
    #     liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
    #     liquidity_aml_dict.update({'account_id':account.id})
    #     aml_obj.create(liquidity_aml_dict)
    #
    #     move.post()
    #     return move

    def post(self):
        if self.payment_difference_handling == 'reconcile':
            amount = self.amount_default + self.amount_1 + self.amount_2 + self.amount_3 + self.amount_4 + self.amount_5
            amount1 = self.amount_1 + self.amount_2 + self.amount_3 + self.amount_4 + self.amount_5
            if self.partner_type == 'supplier' and self.amount_default > self.amount:
                amount1 *= -1

            if self.amount != amount and self.amount_default < self.amount:
                raise ValidationError(_("The total amount that will be posted should equal to the payment amount."))
            elif amount1 != self.payment_difference and self.amount_default > self.amount:
                raise ValidationError(_("The total amount that will be posted should equal to the payment difference."))

            # 1
            self.writeoff_account_id = self.writeoff_account_id_1
            self.payment_difference = 0

            res = super(AccountPayment, self).post()
            amount = self.amount_1 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
            if self.amount_default < self.amount:
                amount *= -1
            move = self._create_payment_entry_with_account(amount, self.writeoff_account_id)

            if self.multiple_post_line == 0:
                return res

            # 2
            self.writeoff_account_id = self.writeoff_account_id_2
            amount = self.amount_2 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
            if self.amount_default < self.amount:
                amount *= -1
            move = self._create_payment_entry_with_account(amount, self.writeoff_account_id)
            if self.multiple_post_line == 1:
                return res

            # 3
            self.writeoff_account_id = self.writeoff_account_id_3
            amount = self.amount_3 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
            if self.amount_default < self.amount:
                amount *= -1
            move = self._create_payment_entry_with_account(amount, self.writeoff_account_id)
            if self.multiple_post_line == 2:
                return res

            # 4
            self.writeoff_account_id = self.writeoff_account_id_4
            amount = self.amount_4 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
            if self.amount_default < self.amount:
                amount *= -1
            move = self._create_payment_entry_with_account(amount, self.writeoff_account_id)
            if self.multiple_post_line == 3:
                return res

            # 5
            self.writeoff_account_id = self.writeoff_account_id_5
            amount = self.amount_5 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
            if self.amount_default < self.amount:
                amount *= -1
            move = self._create_payment_entry_with_account(amount, self.writeoff_account_id)
            if self.multiple_post_line == 4:
                return res
            self.multiple_post_line = 0

        else:
            res = super(AccountPayment, self).post()
            return res

    def _create_payment_entry_with_account(self, amount, account):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            #if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)

        # move = aml_obj.sudo().search([('payment_id', '=', self.id)],limit=1).move_id
        move = last_move = self.env['account.move'].sudo().search([('ref', '=', self.communication)], limit=1, order='id desc')
        # move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        # counterpart_aml = aml_obj.create(counterpart_aml_dict)
        counterpart_aml = aml_obj.sudo().search(
            [('move_id', '=', move.id), ('account_id', '=', counterpart_aml_dict['account_id'])], limit=1, order='id desc')
        if counterpart_aml:
            counterpart_aml.reconciled = False
            self._cr.execute(
                'UPDATE account_move SET state = %s ' 'WHERE id = %s',
                ('draft', move.id))
            counterpart_aml_dict['debit'] += counterpart_aml.debit
            counterpart_aml_dict['credit'] += counterpart_aml.credit
            counterpart_aml.sudo().write(counterpart_aml_dict)
        else:
            counterpart_aml = aml_obj.create(counterpart_aml_dict)

        counterpart_aml.reconciled = False
        self.invoice_ids.register_payment(counterpart_aml)
        counterpart_aml.reconciled = True

        # Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        liquidity_aml_dict.update({'account_id':account.id})
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move

    @api.multi
    def show_new_post_payment(self):
        if self.multiple_post_line != 4:
            self.multiple_post_line += 1
        return {
            "type": "ir.actions.do_nothing",
        }

