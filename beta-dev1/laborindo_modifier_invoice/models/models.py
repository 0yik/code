# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    invoice__no = fields.Char('Invoice No', compute='_compute_invoice_no')
    transaction_no = fields.Char('Transaction No')

    @api.one
    @api.depends('transaction_no', 'efaktur_id')
    def _compute_invoice_no(self):
        if self.transaction_no and self.efaktur_id.name:
            self.invoice__no = self.transaction_no + '.'+ self.efaktur_id.name
        else:
            self.invoice__no = " "

    # stamp = fields.Monetary(string='Stamp',compute='_compute_amount_stamp',store=True)
    #
    # @api.one
    # @api.depends('amount_total')
    # def _compute_amount_stamp(self):
    #     self.stamp = 0
    #     if self.sale_order_id and self.advance_payment_method not in ['fixed','percentage']:
    #         if self.sale_order_id.amount_total < 250000:
    #             self.stamp = 0
    #         elif self.sale_order_id.amount_total >= 250000 and self.sale_order_id.amount_total <= 1000000:
    #             self.stamp = 3000
    #         else:
    #             self.stamp = 6000


