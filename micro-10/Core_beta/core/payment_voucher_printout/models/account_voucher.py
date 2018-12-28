# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'


    payment_voucher_no = fields.Char(string="Payment Voucher No.", default=lambda self: self.env['ir.sequence'].next_by_code('payment.voucher'))
    # account_journal_bank_id = fields.Many2one('account.journal', 'Bank Account', domain="[('type', '=', 'bank')]")
    cheque_no = fields.Char('Cheque No')
    checked_by = fields.Char('Checked By')
    approved_by = fields.Char('Approved By')
    posted_user_id = fields.Many2one('res.users', "Posted By")
    
    
    @api.multi
    def action_move_line_create(self):
        res = super(AccountVoucher, self).action_move_line_create()
        for voucher in self:
            voucher.posted_user_id = self.env.uid
        return res

