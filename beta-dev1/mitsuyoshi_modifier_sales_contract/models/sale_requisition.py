# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class sale_requisition_inherit(models.Model):
    _inherit = 'sale.requisition'

    @api.depends('line_ids.sub_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.line_ids:
                amount_untaxed += line.sub_total
            order.update({
                'amount_total': amount_untaxed + amount_tax,
            })

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                   help="Pricelist for current purchase order.")

    currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True, required=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')

    @api.onchange('currency_id')
    def onchange_product_id(self):
        for record in self.line_ids:
            record.currency_id = self.currency_id


class sale_requisition_inherit(models.Model):
    _inherit = 'sale.requisition.line'

    currency_id = fields.Many2one("res.currency", related='requisition_id.currency_id', store=True, string='Currency', readonly=True)
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])



    @api.multi
    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if self.requisition_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.requisition_id.pricelist_id.id).price
        price, rule_id = self.requisition_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0,
                                                                           self.requisition_id.partner_id)
        pricelist_item = self.env['product.pricelist.item'].browse(rule_id)
        if (pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'with_discount'):
            price, rule_id = pricelist_item.base_pricelist_id.get_product_price_rule(self.product_id,
                                                                                     self.product_uom_qty or 1.0,
                                                                                     self.requisition_id.partner_id)
            return price
        else:
            from_currency = self.requisition_id.company_id.currency_id
            return from_currency.compute(product.lst_price, self.requisition_id.pricelist_id.currency_id)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if self.requisition_id and self.requisition_id.currency_id:
            self.currency_id = self.requisition_id.currency_id

        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product = self.product_id.with_context(
            lang=self.requisition_id.partner_id.lang,
            partner=self.requisition_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.requisition_id.ordering_date,
            pricelist=self.requisition_id.pricelist_id.id
        )

        result = {'domain': domain}

        if self.requisition_id.pricelist_id and self.requisition_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product),
                                                                                 product.taxes_id, self.tax_id)
        self.update(vals)


    @api.onchange('product_uom_id', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom_id or not self.product_id:
            self.price_unit = 0.0
            return

        if self.requisition_id.pricelist_id and self.requisition_id.partner_id:
            product = self.product_id.with_context(
                lang=self.requisition_id.partner_id.lang,
                partner=self.requisition_id.partner_id.id,
                quantity=self.product_uom_qty,
                date=self.requisition_id.ordering_date,
                pricelist=self.requisition_id.pricelist_id.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product),
                                                                              product.taxes_id, self.tax_id)
