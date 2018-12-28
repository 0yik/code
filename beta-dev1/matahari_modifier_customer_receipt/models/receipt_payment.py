from odoo import models, fields, api, _


class ReceiptPaymentLines(models.Model):
    _name = 'receipt.payment.line'

    receipt_payment_id = fields.Many2one('receipt.payment', 'Receipt Payment')
    account_payment_id = fields.Many2one('account.payment', 'Payment')
    referensi = fields.Char(string='Referensi')
    amount = fields.Monetary(string='Amount')
    date = fields.Date(string='Date')
    journal_id = fields.Many2one('account.journal', 'Journal')
    currency_id = fields.Many2one('res.currency', string='Currency',
          default=lambda self: self.env.user.company_id.currency_id.id)
    pay_uisng = fields.Selection(related='receipt_payment_id.pay_uisng', string='Pay Type')


class ReceiptPayment(models.Model):
    _inherit = 'receipt.payment'

    pay_uisng = fields.Selection([('check1', 'Check1'), ('check2', 'Check2')], default='check1', string='Pay Type')
    receipt_payment_line_ids = fields.One2many('receipt.payment.line', 'receipt_payment_id',
           copy=False, string='Payment Lines')
    date = fields.Date('Date', copy=False, help='Effective date for accounting entries',
                       default=fields.Date.context_today, required=False)
    journal_id = fields.Many2one('account.journal', required=False, domain=[('type', 'in', ('bank', 'cash'))], string='Payment Method')
    currency_id = fields.Many2one('res.currency', string='Currency', required=False,
          default=lambda self: self.env.user.company_id.currency_id.id)

    @api.multi
    def load_data1(self):
        line_lst = []
        if self.partner_id:
            account_payment_obj = self.env['account.payment'].sudo()
            domain = [('partner_type', '=', 'customer'),('payment_type','=','inbound'),
                      ('uang_payment','=',True),('state','=','posted'), ('partner_id', '=', self.partner_id.id)]
            uang_payments = account_payment_obj.search(domain)
            for one_uang_payment in uang_payments:
                receipt_payment_line_vals = {
                    'receipt_payment_id': self.id or False,
                    'account_payment_id': one_uang_payment.id or False,
                    'journal_id': one_uang_payment.journal_id and one_uang_payment.journal_id.id or False,
                    'referensi': one_uang_payment.communication or '',
                    'amount': one_uang_payment.amount or 0.00,
                }
                line_lst.append((0, 0, receipt_payment_line_vals))

            account_move_line_obj = self.env['account.move.line'].sudo()
            domain_move_line = [
                ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id),
                ('reconciled', '=', False), ('amount_residual', '!=', 0.0)]
            payment_ids = []
            for one_move_line in account_move_line_obj.search(domain_move_line):
                if one_move_line.payment_id:
                    payment_ids.append(one_move_line.payment_id.id)
            list(set(payment_ids))
            if payment_ids:
                domain = [('id', 'in', payment_ids), ('state', '=', 'posted'), ('uang_payment','=',False)]
                uang_payments = account_payment_obj.search(domain)
                for one_uang_payment in uang_payments:
                    domain_move_line = [('payment_id', '=', one_uang_payment.id), ('credit', '>', 0), ('debit', '=', 0), ('reconciled', '=', False), ('amount_residual', '!=', 0.0)]
                    amount = 0.00
                    journal_id = False
                    for one_line in account_move_line_obj.search(domain_move_line):
                        amount = abs(one_line.amount_residual)
                        journal_id = one_line.journal_id and one_line.journal_id.id or False

                    if amount:
                        receipt_payment_line_vals = {
                            'receipt_payment_id': self.id or False,
                            'account_payment_id': one_uang_payment.id or False,
                            'journal_id': journal_id,
                            'referensi': one_uang_payment.communication or '',
                            'amount': amount,
                        }
                        line_lst.append((0, 0, receipt_payment_line_vals))

        return line_lst

    # @api.onchange('partner_id')
    # def onchange_account_id1(self):
    #     self.receipt_payment_line_ids = False
    #     if self.partner_id:
    #         self.receipt_payment_line_ids = self.load_data1()

