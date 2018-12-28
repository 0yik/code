# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _

class ReceiptPayment(models.Model):
    _inherit = 'receipt.payment'

    payment_voucher_no = fields.Char(
        string="Payment Voucher No.",
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'receipt.payment'))
    cheque_no = fields.Char('Cheque No')
    checked_by = fields.Char('Checked By')
    approved_by = fields.Char('Approved By')
    posted_user_id = fields.Many2one('res.users', "Posted By")

    @api.multi
    def action_post(self):
        res = super(ReceiptPayment, self).action_post()
        for receipt in self:
            receipt.posted_user_id = self.env.uid
        return res
    

ReceiptPayment()
