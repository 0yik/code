# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    service_charge_id = fields.Many2one('service.charge', string = 'Service Charge')

class PosOrder(models.Model):
    _inherit= "pos.order"

    service_charge = fields.Boolean('Apply Service Charge?')
    amount_service = fields.Float(compute='_compute_amount_all', string='Service Charge', digits=0)

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a pos order.
        """
        result = super(PosOrder, self)._prepare_invoice()
        result['service_charge'] = self.service_charge
        result['amount_service'] = self.amount_service
        return result

    def _action_create_invoice_line(self, line=False, invoice_id=False):
        inv_line = super(PosOrder, self)._action_create_invoice_line(line=line, invoice_id=invoice_id)
        inv_line.service_charge_value = line.service_charge_value
        inv_line.subtotal_service_charge_value = line.subtotal_service_charge_value
        return inv_line

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):
        super(PosOrder, self)._compute_amount_all()
        for order in self:
            if order.service_charge:
                order.amount_service = sum(line.subtotal_service_charge_value for line in order.lines)
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['service_charge'] = ui_order.get('service_charge')
        return res

    @api.model
    def _amount_line_tax(self, line, fiscal_position_id):
        if not line.order_id.service_charge:
            return super(PosOrder, self)._amount_line_tax(line, fiscal_position_id)
        taxes = line.tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id)
        if fiscal_position_id:
            taxes = fiscal_position_id.map_tax(taxes, line.product_id, line.order_id.partner_id)
        price = (line.price_unit * (1 - (line.discount or 0.0) / 100.0)) + line.service_charge_value
        taxes = taxes.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)['taxes']
        return sum(tax.get('amount', 0.0) for tax in taxes)

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    service_charge_value = fields.Float(compute='_compute_amount_line_all', string='Service Charge', digits=0)
    subtotal_service_charge_value = fields.Float(compute='_compute_amount_line_all', string='Subtotal Service Charge', digits=0)

    @api.depends('price_unit', 'tax_ids', 'qty', 'discount', 'product_id', 'order_id.service_charge')
    def _compute_amount_line_all(self):
        for line in self:
            if not line.order_id.service_charge:
                line.service_charge_value = 0.0
                line.subtotal_service_charge_value = 0.0
                super(PosOrderLine, line)._compute_amount_line_all()
                continue
            service_charge = 0
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.order_id.service_charge and line.product_id.service_charge_id:
                if line.product_id.service_charge_id.service_charge_computation=='fixed':
                    line.service_charge_value = line.product_id.service_charge_id.amount
                else:
                    line.service_charge_value = ((price * line.product_id.service_charge_id.amount) / 100)
            else:
                line.service_charge_value = 0.0
            fpos = line.order_id.fiscal_position_id
            tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, line.order_id.partner_id) if fpos else line.tax_ids
            price += line.service_charge_value
            line.subtotal_service_charge_value = line.service_charge_value * line.qty
            taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_subtotal_incl': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    service_charge = fields.Boolean('Apply Service Charge?')
    amount_service = fields.Float(string='Service Charge', digits=0)

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        print "gggggggg",self.amount_total

    @api.multi
    def get_taxes_values(self):
        if not self.service_charge:
            return super(AccountInvoice, self).get_taxes_values()
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = (line.price_unit * (1 - (line.discount or 0.0) / 100.0)) ++ line.service_charge_value
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    service_charge_value = fields.Float(string='Service Charge', digits=0)
    subtotal_service_charge_value = fields.Float(string='Subtotal Service Charge', digits=0)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'service_charge_value')
    def _compute_price(self):
        if not self.invoice_id.service_charge:
            return super(AccountInvoiceLine, self)._compute_price()
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = (self.price_unit * (1 - (self.discount or 0.0) / 100.0)) + self.service_charge_value
        print "PRICE   ",price
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
