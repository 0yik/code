# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    other_invoice = fields.Boolean("Other Invoice")
    other_bills = fields.Boolean("Other Bills")

    @api.model
    def create(self, vals):
    	if self._context.get('type',False) == 'out_invoice' and self._context.get('type_inv', False):
    		vals.update({'other_invoice':True})

    	if self._context.get('type',False) == 'in_invoice' and self._context.get('type_bill', False):
    		vals.update({'other_bills':True})
    	return super(AccountInvoice, self).create(vals)

    # @api.multi
    # def action_move_create(self):
    #     values = super(AccountInvoice, self).action_move_create()
    #     for inv in self:
    #         if inv.other_invoice:
    #             number = self.env['ir.sequence'].next_by_code('other.invocie.sequence')
    #             inv.move_name = number
    #         if inv.other_bills:
    #             number = self.env['ir.sequence'].next_by_code('other.bills.sequence')
    #             inv.move_name = number
    #     return values


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        values = super(AccountMove, self).post()
        new_name = False
        invoice = self._context.get('invoice', False)
        for move in self:
            if move.name == '/':
                new_name = False
            if invoice and invoice.other_invoice and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('other.invocie.sequence')
            if invoice and invoice.other_bills and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('other.bills.sequence')
            if new_name:
                move.name = new_name
        return values
