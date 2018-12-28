# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchasePaymentVoucher(models.Model):
    
    _name = 'purchase.payment.voucher'

#     @api.model
#     def _default_company(self):
#         return self.env.user.company_id

    @api.onchange('line_ids.amount')
    @api.depends('line_ids.amount')
    def _compute_amount(self):
        amount = 0.00
        for rec in self.line_ids:
            amount += rec.amount 
        self.total_amount = amount

    @api.onchange('account_voucher_ids', 'vendor_bill_ids')
    @api.depends('account_voucher_ids', 'vendor_bill_ids')
    def _compute_line_ids(self):
        invoice_information_ids = []
        if self.vendor_bill_ids or self.account_voucher_ids:
            for vendor_bill_id in self.vendor_bill_ids:
                for invoice_line_id in vendor_bill_id.invoice_line_ids:
                    invoice_information_ids.append(self.env['invoice.information'].new({
                        'invoice_date': vendor_bill_id.date_invoice,
                        'invoice_number': vendor_bill_id.number,
                        'account_invoice_line_id': invoice_line_id.id,
                        'product_id': invoice_line_id.product_id.id,
                        'amount': invoice_line_id.price_subtotal,
                    }).id)
            for account_voucher_id in self.account_voucher_ids:
                for line_id in account_voucher_id.line_ids:
                    invoice_information_ids.append(self.env['invoice.information'].new({
                        'invoice_date': account_voucher_id.date,
                        'invoice_number': account_voucher_id.number,
                        'account_voucher_line_id': line_id.id,
                        'product_id': line_id.product_id.id,
                        'amount': line_id.price_subtotal,
                    }).id)
            
            self.line_ids = self.env['invoice.information'].browse(invoice_information_ids)
        if not self.vendor_bill_ids and not self.account_voucher_ids:
            self.line_ids = []


    name = fields.Many2one('res.partner', 'Payee Name', required=True)
    date = fields.Date('Date', required=True)
    number = fields.Char('PV Number')
    payment_method = fields.Char('Payment Method')
    payment_account_id = fields.Many2one('account.account', 'Payment Account')
    bank_id = fields.Many2one('account.journal', 'Bank')
    cheque_number =  fields.Char('Cheque Number')
    cheque_date = fields.Date('Cheque Date')
    vendor_bill_ids = fields.Many2many('account.invoice', string='Vendor Bills')
    account_voucher_ids = fields.Many2many('account.voucher', string='Expenses')
    currency_id = fields.Many2one('res.currency', 'Currency')
    remarks = fields.Text('Remarks')
    total_amount = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_amount')
    line_ids = fields.One2many('invoice.information', 'purchase_payment_voucher_id', 'Invoice Information')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('draft','Draft'),
        ('submitted','Submitted'),
        ('verified','Verified'),
        ('approved','Approved'),
        ('cancelled','Cancelled'),
    ], default='draft')
    prepared_by = fields.Many2one('res.users')
    checked_by = fields.Many2one('res.users')
    posted_by = fields.Many2one('res.users')
    received_by = fields.Many2one('res.users')
    approved_by = fields.Many2one('res.users')
    
    
    
    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('vendor_bill_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    @api.multi
    def action_view_voucher(self):
        vouchers = self.mapped('account_voucher_ids')
        action = self.env.ref('account_voucher.action_purchase_receipt').read()[0]
        if len(vouchers) > 1:
            action['domain'] = [('id', 'in', vouchers.ids)]
        elif len(vouchers) == 1:
            action['views'] = [(self.env.ref('account_voucher.view_purchase_receipt_form').id, 'form')]
            action['res_id'] = vouchers.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    @api.multi
    def draft_voucher(self):
        for rec in self:
            rec.write({
                'state': 'draft'
            })
        return True
    
    @api.multi
    def submit_voucher(self):
        for rec in self:
            vals = {'state': 'submitted', 'prepared_by': self._uid} 
            if not rec.number:
                vals.update({'number': self.env['ir.sequence'].next_by_code('purchase.payment.voucher')})
            rec.write(vals)
        return True
    
    @api.multi
    def verify_voucher(self):
        for rec in self:
            rec.write({
                'state': 'verified',
                'checked_by': self._uid,
            })
        return True
    
    @api.multi
    def approve_voucher(self):
        for rec in self:
            rec.write({
                'state': 'approved',
                'approved_by': self._uid,
            })
        return True
    
    @api.multi
    def cancel_voucher(self):
        for rec in self:
            rec.write({
                'state': 'cancelled'
            })
        return True
            
            
class InvoiceInformation(models.Model):
    
    _name = 'invoice.information'
    
    purchase_payment_voucher_id = fields.Many2one('purchase.payment.voucher', 'Payee Name')
    invoice_date = fields.Date('Invoice Date', readonly=True)
    invoice_number = fields.Char('Invoice Number', readonly=True)
    product_id = fields.Many2one('product.product', 'Product')
    amount = fields.Float('Amount')
    account_invoice_line_id = fields.Many2one('account.invoice.line')
    account_voucher_line_id = fields.Many2one('account.voucher.line')
