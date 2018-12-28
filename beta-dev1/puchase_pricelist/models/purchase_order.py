
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class purchase_order(models.Model):
	_inherit = 'purchase.order'


	@api.onchange('pricelist_id')
	def onchange_pricelist(self):
		if self.pricelist_id:
			for line in self.order_line:
				line.price_unit = self.pricelist_id.price_get(line.product_id.id,
										line.product_qty, self.partner_id.id)[self.pricelist_id.id]


	@api.depends('order_line.price_total')
	def _amount_all(self):
		for order in self:
			amount_untaxed = amount_tax = 0.0
			for line in order.order_line:
				amount_untaxed += line.price_subtotal
				# FORWARDPORT UP TO 10.0
				if order.company_id.tax_calculation_rounding_method == 'round_globally':
					taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty,
													  product=line.product_id, partner=line.order_id.partner_id)
					amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
				else:
					amount_tax += line.price_tax
			order.update({
				'amount_untaxed': order.currency_id.round(amount_untaxed),
				'amount_tax': order.currency_id.round(amount_tax),
				'amount_total': amount_untaxed + amount_tax,
			})

	pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True,
				states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current purchase order.")

	currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True,
								  required=True)

	product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)

	@api.onchange('partner_id')
	def onchange_partner(self):
		values = {
			'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
		}
		self.update(values)

	@api.model
	def create(self, vals):
		# Makes sure 'pricelist_id' are defined
		if any(f not in vals for f in ['pricelist_id']):
			partner = self.env['res.partner'].browse(vals.get('partner_id'))
			vals['pricelist_id'] = vals.setdefault('pricelist_id',partner.property_product_pricelist and partner.property_product_pricelist.id)
		result = super(purchase_order, self).create(vals)
		return result



class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	@api.multi
	def _get_display_price(self, product):
		if self.order_id.pricelist_id.discount_policy == 'with_discount':
			return product.with_context(pricelist=self.order_id.pricelist_id.id).price
		price, rule_id = self.order_id.pricelist_id.get_product_price_rule(self.product_id, self.product_qty or 1.0,
																		   self.order_id.partner_id)
		pricelist_item = self.env['product.pricelist.item'].browse(rule_id)
		if (pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'with_discount'):
			price, rule_id = pricelist_item.base_pricelist_id.get_product_price_rule(self.product_id,
																					 self.product_qty or 1.0,
																					 self.order_id.partner_id)
			return price
		else:
			from_currency = self.order_id.company_id.currency_id
			return from_currency.compute(product.lst_price, self.order_id.pricelist_id.currency_id)

	@api.multi
	@api.onchange('product_id')
	def product_id_change(self):

		if not self.product_id:
			return {'domain': {'product_uom': []}}
		vals = {}

		product = self.product_id.with_context(
			lang=self.order_id.partner_id.lang,
			partner=self.order_id.partner_id.id,
			quantity=vals.get('product_qty') or self.product_qty,
			date=self.order_id.date_order,
			pricelist=self.order_id.pricelist_id.id,
			uom=self.product_uom.id
		)

		if self.order_id.pricelist_id and self.order_id.partner_id:
			vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product),
																				 product.taxes_id, self.taxes_id)
		self.update(vals)


	@api.onchange('product_uom', 'product_qty')
	def product_uom_change(self):
		if not self.product_uom or not self.product_id:
			self.price_unit = 0.0
			return

		if self.order_id.pricelist_id and self.order_id.partner_id:
			product = self.product_id.with_context(
				lang=self.order_id.partner_id.lang,
				partner=self.order_id.partner_id.id,
				quantity=self.product_qty,
				date=self.order_id.date_order,
				pricelist=self.order_id.pricelist_id.id,
				uom=self.product_uom.id,
				fiscal_position=self.env.context.get('fiscal_position')
			)
			self.price_unit = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product),
																			  product.taxes_id, self.taxes_id)


			#self.price_subtotal = self.product_qty * self.price_unit



