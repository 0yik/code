# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import exceptions
from datetime import datetime


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    def compounding_payment_amount(self, amount_due, overdue_percentage, time):
        amount = amount_due
        payment_charge = 0
        for i in range(0, time):
            payment_charge = ((amount * overdue_percentage) / 100)
            amount += ((amount * overdue_percentage) / 100)
        return payment_charge
    def overdue_payment_charge(self):
        invoices = self.search([('state', '=', 'open'), ('date_due', '!=', False)])
        for invoice in invoices:
            overdue_payment_amount = 0.0
            overdue_payment_line = False
            amount_due = 0.0
            today = datetime.today().date()
            date_due = datetime.strptime(invoice.date_due, '%Y-%m-%d').date()
            if invoice.invoice_line_ids and invoice.payment_term_id:
                payment_term_id = invoice.payment_term_id
                for line in invoice.invoice_line_ids:
                    if line.product_id and line.product_id.name == 'Overdue Payment Charge':
                        amount_due = invoice.amount_untaxed - line.price_subtotal
                        overdue_payment_line = line
                    else:
                        amount_due = invoice.amount_untaxed
                if date_due < today:
                    day = (today - date_due).days
                    time = round(float(day) / 30, 0) or 1
                    if payment_term_id.overdue_charges_type == 'amount':
                        if payment_term_id.overdue_type == 'daily':
                            overdue_payment_amount = day * payment_term_id.rate
                        elif payment_term_id.overdue_type == 'monthly':
                            time = round(float(day)/30, 0)
                            if time == 0:
                                overdue_payment_amount = payment_term_id.rate
                            else:
                                overdue_payment_amount = time * payment_term_id.rate


                    elif payment_term_id.overdue_charges_type == 'percentage':
                        if payment_term_id.overdue_type == 'daily':
                            if payment_term_id.computation_method == 'linear':
                                overdue_payment_amount = day * payment_term_id.overdue_percentage
                            elif payment_term_id.computation_method == 'compounding':
                                overdue_payment_amount = self.compounding_payment_amount(amount_due, payment_term_id.overdue_percentage, day)
                        elif payment_term_id.overdue_type == 'monthly':
                            if payment_term_id.computation_method == 'linear':
                                overdue_payment_amount = time * payment_term_id.overdue_percentage
                            elif payment_term_id.computation_method == 'compounding':
                                overdue_payment_amount = self.compounding_payment_amount(amount_due, payment_term_id.overdue_percentage, time)

                    if not overdue_payment_line:
                        product_id = self.env['product.product'].search([('name', '=', 'Overdue Payment Charge')], limit=1)
                        data = {
                            'product_id': product_id.id,
                            'name' : product_id.name,
                            'quantity' : 1,
                            'price_unit' : overdue_payment_amount,
                            'price_subtotal': overdue_payment_amount,
                            'account_id': self.env['account.invoice.line'].get_invoice_line_account(invoice.type, product_id, invoice.fiscal_position_id, invoice.company_id).id or False,
                            'invoice_id': invoice.id
                        }
                        invoice.write({
                            'state': 'draft'
                        })
                        order_line = self.env['account.invoice.line'].create(data)
                        invoice.move_id = False
                        invoice.action_invoice_open()

                    else:
                        invoice.write({
                            'state': 'draft'
                        })
                        overdue_payment_line.price_subtotal = overdue_payment_amount
                        overdue_payment_line.price_unit = overdue_payment_amount
                        invoice.move_id = False
                        invoice.action_invoice_open()