# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class recurring_invoice_line(models.Model):
    _name = 'recurring.invoice.line'

    name = fields.Text(string='Description', required=True)

    recurring_invoice_id = fields.Many2one('recurring.invoice', string='recurring invoice')

    origin = fields.Char(string='Source Document',
                         help="Reference of the document that produced this invoice.")
    sequence = fields.Integer(default=10,
                              help="Gives the sequence of this line when displaying the invoice.")

    uom_id = fields.Many2one('product.uom', string='Unit of Measure',
                             ondelete='set null', index=True, oldname='uos_id')
    product_id = fields.Many2one('product.product', string='Product',
                                 ondelete='restrict', index=True)
    account_id = fields.Many2one('account.account', string='Account',required=True, domain=[('deprecated', '=', False)],
                                 help="The income or expense account related to the selected product.")
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))

    price_subtotal = fields.Monetary(string='Amount',store=True, readonly=True, compute='_compute_price')
    price_subtotal_signed = fields.Monetary(string='Amount Signed', currency_field='company_currency_id',store=True, readonly=True)
    
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
                            required=True, default=1)
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'),
                            default=0.0)
    invoice_line_tax_ids = fields.Many2many('account.tax',
                                            'recurring_account_invoice_line_tax', 'invoice_line_id', 'tax_id',
                                            string='Taxes',
                                            domain=[('type_tax_use', '!=', 'none'), '|', ('active', '=', False),
                                                    ('active', '=', True)], oldname='invoice_line_tax_id')

    account_analytic_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')


    partner_id = fields.Many2one('res.partner', string='Partner',
                                 related='recurring_invoice_id.partner_id', store=True, readonly=True)

    currency_id = fields.Many2one('res.currency', related='recurring_invoice_id.currency_id', store=True)

    company_currency_id = fields.Many2one('res.currency', related='recurring_invoice_id.company_currency_id', readonly=True,
                                          related_sudo=False)

    company_id = fields.Many2one('res.company', string='Company',
                                 related='recurring_invoice_id.company_id', store=True, readonly=True)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'recurring_invoice_id.partner_id', 'recurring_invoice_id.currency_id', 'recurring_invoice_id.company_id')
    def _compute_price(self):
        currency = self.recurring_invoice_id and self.recurring_invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,partner=self.recurring_invoice_id.partner_id)
        self.price_subtotal = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_subtotal_signed = taxes['total_included'] if taxes else self.quantity * price