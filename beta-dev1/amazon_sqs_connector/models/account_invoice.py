# -*- coding: utf-8 -*-

import base64
import urllib2
import datetime
import boto3
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    sales_channel = fields.Char('Sales Channel', readonly=False)
    store_url = fields.Char('Store url', readonly=False)
    shipping_id = fields.Many2one(
        "shipping.address", string='Shipping Address', readonly=True, copy=False)
    billing_id = fields.Many2one(
        "billing.address", string='Billing Address', readonly=True, copy=False)
    mums_order_id = fields.Char('Order ID')
    cus_email = fields.Char('Email')
    cus_phone = fields.Char('Phone')
    shipping_charges = fields.Monetary('Shipping Charges')
    discount_amount = fields.Monetary('Coupon Discount')
    extra_delivery = fields.Monetary('Extra Delivery')
    payment_method = fields.Char('Payment Method', help="Payment Method")
    so_id = fields.Many2one("sale.order", string='SO id')
    po_id = fields.Many2one("purchase.order", string='PO id')
    # number=fields.Char('Reference Number')

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax + self.shipping_charges + self.discount_amount
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    suppliers = fields.Many2one('res.partner', 'Suppliers')
    source_id = fields.Many2one('stock.location', 'Source')
    warehouse_id = fields.Char(string='Warehouse Id', help='Warehouse Id')
    sqs_product_id = fields.Char(string='Product Id', help='Product Id.')
    sqs_supplier_id = fields.Char(string='Supplier Id', help='Supplier Id.')


