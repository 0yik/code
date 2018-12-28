# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class account_invoice(models.Model):
    _inherit = 'account.invoice.line'

    last_sold_price = fields.Float('Last Sold Price')
    last_sold_date = fields.Date('Last Sold Date')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id  and self.invoice_id and self.invoice_id.partner_id:
            account_invoices = self.env['account.invoice'].search([('partner_id', '=', self.invoice_id.partner_id.id)], order='create_date desc')
            for account_invoice in account_invoices:
                is_find = False
                for invoice_line in account_invoice.invoice_line_ids:
                    if invoice_line.product_id == self.product_id:
                        self.last_sold_price = invoice_line.price_unit
                        self.last_sold_date = account_invoice.date_invoice
                        is_find = True
                if is_find: break
            if not self.last_sold_price:
                self.last_sold_price = self.price_unit
            if not self.last_sold_date:
                self.last_sold_date = datetime.now()


