# -*- coding: utf-8 -*-

from odoo import models, fields, api

class multi_discount_pricelist(models.Model):
    _inherit = "product.pricelist.item"

    compute_price = fields.Selection([
        ('fixed', 'Fix Price'),
        ('percentage', 'Percentage (discount)'),
        ('multi_disc', 'Multi Discount'),
        ('formula', 'Formula')], index=True, default='fixed')
    multi_discount = fields.Char('Multi Discounts')

    @api.onchange('multi_discount')
    def _onchange_multi_discount(self):
        def get_disocunt(percentage,amount):
            new_amount = (percentage * amount)/100
            return (amount - new_amount)
        if self.multi_discount:
            amount = 100
            splited_discounts = self.multi_discount.split("+")
            if ',' in self.multi_discount:
                raise UserError("You cannot use comma to separate discounts. Please add multiple discounts with '+' notation. \n For example 20 + 5.2")
            for disocunt in splited_discounts:
                amount = get_disocunt(float(disocunt),amount)
            self.discount = 100 - amount
        else:
            self.discount = 0

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        for line in self.order_id.pricelist_id.item_ids:
            if line.compute_price=='multi_disc':
                if line.multi_discount:
                    if self.product_id.product_tmpl_id.id == line.product_tmpl_id.id:
                        self.multi_discount=line.multi_discount
	if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        return result

class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _fix_tax_included_price_company(self, price, prod_taxes, line_taxes, company_id):
        if company_id:
            #To keep the same behavior as in _compute_tax_id
            prod_taxes = prod_taxes.filtered(lambda tax: tax.company_id == company_id)
            line_taxes = line_taxes.filtered(lambda tax: tax.company_id == company_id)
        return self._fix_tax_included_price(price, prod_taxes, line_taxes)
