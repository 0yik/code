# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def validate_delivery_invoice(self):
        for record in self:
            payment_method = self.env.ref('account.account_payment_method_manual_in')
            payment_data = self.env['account.payment'].with_context(default_invoice_ids=[(4, record.id, None)]).default_get(
                ['communication', 'currency_id', 'invoice_ids', 'payment_difference', 'partner_id',
                 'payment_method_id', 'payment_difference_handling', 'journal_id', 'state', 'writeoff_account_id',
                 'payment_date', 'partner_type', 'payment_token_id', 'hide_payment_method', 'payment_method_code',
                 'amount', 'payment_type'])
            pay_journal = self.env['account.journal'].sudo().search([('type', '=', 'cash')], limit=1)
            payment_data.update({'journal_id': pay_journal.id,
                                     'payment_method_id': payment_method and payment_method.id,
                                     })
            payment = self.env['account.payment'].sudo().with_context(active_model='account.invoice',active_ids=record.id).create(payment_data)
            record.reconciled = True
            payment.post()
            order = self.env['sale.order'].search([('name', '=', record.origin)], limit=1)
            if order:
                self.env['pos.order'].with_context({'by_delivery':True}).reduce_bom_stock(order)
        return True

    @api.model
    def get_list_invoice(self, domain=[]):
        domains = [('state', '=', 'open'), ('name', '=', 'Point of sale')]
        domains.extend(domain)
        invoices = self.env['account.invoice'].search(domains, limit=100)
        invoice_list = []
        for invoice in invoices:
            invoice_list.append(invoice.convert_to_json())
        return invoice_list

    @api.model
    def get_delivery_product_id(self):
        delivery_product = self.env.ref('delivery_orders_kds.product_delivery')
        return {
            'product_id': delivery_product and delivery_product.id or False,
        }
    @api.model
    def convert_to_json(self):
        delivery_product = self.env.ref('delivery_orders_kds.product_delivery')
        order = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
        return {
            'id': self.id,
            'customer': {
                'id': self.partner_id.id,
                'name': self.partner_id.name,
                'phone': self.partner_id.phone,
                'street': self.partner_id.street,
            },
            'date': self.date_invoice,
            'number': self.number,
            'salesperson': self.user_id.name,
            'date_due': self.date_due,
            'origin': self.origin,
            'category': order and order.category or '',
            'amount_total': self.amount_total,
            'amount_untaxed': self.amount_untaxed,
            'state': self.state,
            'product_id': delivery_product and delivery_product.id or False,
        }


# payment_data = {
#     'invoice_ids': [(6, 0, [record.id])],
#     'amount': record.amount_total,
#     'payment_date': record.date_invoice,
#     'communication': 'Point of sale',
#     'partner_id': record.partner_id.id,
#     'partner_type': record.type in ('out_invoice', 'out_refund') and 'customer' or 'supplier',
#     'journal_id': self.env['account.journal'].search([('type', '=', 'cash')], limit=1).id,
#     'payment_type': 'inbound',
#     'payment_method_id': payment_method.id,
# }
