# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import calendar

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    date_invoice = fields.Date(string='Invoice Date',
        readonly=True, states={'draft': [('readonly', False)]}, index=True,
        help="Keep empty to use the current date", copy=False, default=datetime.today())
    rate = fields.Float(related="currency_id.rate", string="Currency Rate")
    c_number = fields.Char()
    dd_invoice_no = fields.Char("DD Invoice No.")
    season = fields.Char("Season")
    agent = fields.Char("Commision Payable To")
    
    @api.model
    def create(self, values):
        res = super(AccountInvoice, self).create(values)

        year = datetime.now().year
        today_date = datetime.now().strftime("%Y/%m/%d")

        if res.type == 'out_invoice':
            get_sequence = self.env['ir.sequence'].search([('code', '=', 'account.invoice.customer')])
            end_date = "%d/01/01" % year
            if get_sequence.number_next_actual > 0:
                if end_date == today_date:
                    get_sequence.write({'number_next_actual': 0})

            res.c_number = self.env['ir.sequence'].next_by_code('account.invoice.customer')


        if res.type == 'in_invoice':
            get_sequence = self.env['ir.sequence'].search([('code', '=', 'account.invoice.vendor')])
            end_date = "%d/01/01" % year
            if get_sequence.number_next_actual > 0:
                if end_date == today_date:
                    get_sequence.write({'number_next_actual': 0})

            res.c_number = self.env['ir.sequence'].next_by_code('account.invoice.vendor')
        if res.type == 'out_refund':
            get_sequence = self.env['ir.sequence'].search([('code', '=', 'account.invoice.credit')])
            end_date = "%d/01/01" % year
            if get_sequence.number_next_actual > 0:
                if end_date == today_date:
                    get_sequence.write({'number_next_actual': 0})

            res.c_number = self.env['ir.sequence'].next_by_code('account.invoice.credit')
        if res.type == 'in_refund':
            get_sequence = self.env['ir.sequence'].search([('code', '=', 'account.invoice.supp.debit')])
            end_date = "%d/01/01" % year
            if get_sequence.number_next_actual > 0:
                if end_date == today_date:
                    get_sequence.write({'number_next_actual': 0})

            res.c_number = self.env['ir.sequence'].next_by_code('account.invoice.supp.debit')
        if res.type == 'out_invoice' and res.debit_note:
            get_sequence = self.env['ir.sequence'].search([('code', '=', 'account.invoice.debit')])
            end_date = "%d/01/01" % year
            if get_sequence.number_next_actual > 0:
                if end_date == today_date:
                    get_sequence.write({'number_next_actual': 0})

            res.c_number = self.env['ir.sequence'].next_by_code('account.invoice.debit')

        return res
    
    @api.multi
    def name_get(self):
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Vendor Bill'),
            'out_refund': _('Refund'),
            'in_refund': _('Vendor Refund'),
        }
        result = []
        for inv in self:
            result.append((inv.id, "%s" % (inv.c_number or TYPES[inv.type])))
        return result

    _sql_constraints = [
        ('c_number_uniq','UNIQUE (c_number)',  'You can not have two Invoice with the same InvoiceID !'),
    ]

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    po_no = fields.Char("P/O No.")
    margin_required = fields.Char("Margin Required %")
    commision_payable = fields.Char("Commision Payable %")
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['season'] = self.season
        res['agent'] = self.agent
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res['po_no'] = self.shipment_buyer_order_no
        res['margin_required'] = float(self.company_commision) + float(self.agent_commision)
        res['commision_payable'] = self.agent_commision
        return res
    
class ReceiptPayment(models.Model):
    _inherit = 'receipt.payment'
    
    name = fields.Char(default='/', readonly=False, required=True, copy=False, string='Number')
    rate = fields.Float(related="currency_id.rate", string="Currency Rate")
    
    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'You can not have two Payment with the same PaymentID !'),
    ]
    
class AccountMove(models.Model):
    _inherit = "account.move"
    _rec_name = 'j_name'
    
    j_name = fields.Char()
    remark = fields.Char("Remark")
    
    @api.model
    def create(self, values):
        res = super(AccountMove, self).create(values)
        res.j_name = self.env['ir.sequence'].next_by_code('account.move')
        return res
    
    @api.multi
    @api.depends('j_name')
    def name_get(self):
        result = []
        for move in self:
            result.append((move.id, move.j_name))
        return result
    
    _sql_constraints = [
        ('j_name_uniq', 'UNIQUE (j_name)',  'You can not have two Journal Entries with the same JournalID !'),
    ]
    
class AccountVoucher(models.Model):
    _inherit = "account.voucher"
    _rec_name = 'av_number'
    
    av_number = fields.Char()
    cheque_number = fields.Char("Cheque Number")
    cheque_date = fields.Date("Cheque Date")
    remarks = fields.Char("Remarks")
    
    @api.model
    def create(self, values):
        res = super(AccountVoucher, self).create(values)
        if res.voucher_type == 'sale':
            res.av_number = self.env['ir.sequence'].next_by_code('other.income')
        if res.voucher_type == 'purchase':
            res.av_number = self.env['ir.sequence'].next_by_code('account.voucher.expense')
        return res
    
    @api.multi
    @api.depends('av_number')
    def name_get(self):
        return [(r.id, (r.av_number or _('Voucher'))) for r in self]
    
    _sql_constraints = [
        ('av_number_uniq', 'UNIQUE (av_number)',  'You can not have two Expense with the same ExpenseID !'),
    ]
