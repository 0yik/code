# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    actual_crd = fields.Char("Actual CRD")
    attention = fields.Char("Attention")
    remark = fields.Char("Remarks")
    your_po = fields.Char("Your PO")
    reference_no = fields.Many2one('account.invoice', string="Ref No")
    number = fields.Char(related='move_id.name', store=True, readonly=False, copy=False)
    dd_invoice_num = fields.Char(related='reference_no.dd_invoice_no', string="DD Invoice No")
    invoice_date = fields.Date(related='reference_no.date_invoice', string="Invoice Date")
    vendor_season = fields.Char(related='reference_no.season', string="Season")
    commission_payable_to = fields.Char(related='reference_no.agent', string="Commission Payable To")


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    po_no = fields.Char(string='P/O No')
    style_no = fields.Char(string='Style No')
    margin_required = fields.Float(string='Margin Required %')
    commission_payable = fields.Float(string='Commission Payable %')
