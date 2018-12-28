from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	product_code = fields.Char(string='Product Code', required=True)
	# product_brand_id = fields.Many2one('product.brand', string='Brand')

	@api.constrains('product_code')
	def _check_product_code_duplicate(self):
		for record in self:
			product_codes = self.search([('id','!=',self.id)]);
			for product_code in product_codes:
				if str(product_code.product_code).lower() == str(record.product_code).lower():
					raise ValidationError(_('Error ! Product Code is already used.'))

	def create(self, vals):
		if not vals.get('product_code', False):
			vals.update({'product_code': 'None'})
		#TODO: prepare
		if self.env.context.get('import_file'):
			True
		res = super(ProductTemplate, self).create(vals)
		return res

	@api.multi
	def write(self,vals):
		res = super(ProductTemplate, self).write(vals)
		if vals.get('product_code',False):
			variants = self.env['product.product'].search([('product_tmpl_id','=',self.id or False)])
			for product in variants:
				product.write({'product_code':vals.get('product_code',False)})
		return res

class ProductProduct(models.Model):
	_inherit = 'product.product'
	product_code = fields.Char(string='Product Code', required=True)
	origin_price = fields.Float('Sale Price')


	def _compute_product_lst_price(self):
		super(ProductProduct,self)._compute_product_lst_price()
		for product in self:
			if product.origin_price:
				product.lst_price = product.origin_price


	@api.model
	def create(self, vals):
		if not vals.get('lst_price',False):
			vals.update({
				'origin_price': vals.get('list_price')
			})
		if not vals.get('product_tmpl_id', False) and vals.get('product_code', False):
			product_template_id = self.env['product.template'].search([('product_code','=',vals.get('product_code'))],limit=1).id
			vals.update({
				'product_tmpl_id' : product_template_id
			})
		if not vals.get('product_code', False):
			if vals.get('product_tmpl_id', False):
				vals.update(
					{'product_code': self.env['product.template'].browse(vals.get('product_tmpl_id', False)).product_code or ''})
		res = super(ProductProduct, self).create(vals)
		if res.product_tmpl_id and res.product_tmpl_id.product_code == 'None':
			res.product_tmpl_id.product_code = res.product_code

		if res.product_tmpl_id and not res.product_tmpl_id.category_main_id:
			res.product_tmpl_id.category_main_id = res.category_main_id

		if res.product_tmpl_id and not res.product_tmpl_id.category_subfirst_id:
			res.product_tmpl_id.category_subfirst_id = res.category_subfirst_id

		if res.product_tmpl_id and not res.product_tmpl_id.category_subsecond_id:
			res.product_tmpl_id.category_subsecond_id = res.category_subsecond_id
		return res

