# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import Warning
from odoo.tools.translate import _

class ProductPackWizard(models.TransientModel):
	_name = 'purchase.pack.wizard' 	

	product_name = fields.Many2one('product.product',string='PACK',required=True)
	quantity = fields.Integer('Quantity',required=True ,default=1)
	@api.multi
	def purchase_add_product_button(self):
		i=1
		if self._context['active_model']=='purchase.order':
			purchase_obj=self.env['purchase.order'].search([('id', '=', self._context['active_id'])], limit=1)
			date_planned=purchase_obj.date_planned
			product_obj = self.product_name.wk_product_pack
			pack_barcode=self.product_name.barcode
			if self.product_name.taxes_id:
				taxes_id = self.product_name.taxes_id.ids
			for product in product_obj:
				prod=self.env['product.product'].search([('name','=',product.name)])
				self.env['purchase.order.line'].create({'order_id':self._context['active_id'],'product_id':prod.id, 'name':prod.name,'price_unit':prod.price,'product_uom':1,'product_qty':product.product_quantity,'date_planned':date_planned,'pack_barcode':"%s %s"%(str(i),str(pack_barcode)),'taxes_id':[(6, 0, taxes_id)]})
				i=i+1
			return True

	@api.onchange('quantity', 'product_name')
	def onchange_quantity_pack(self):
		if self.quantity:
			if self.product_name:
				for prod in self.product_name.wk_product_pack:
					if self.quantity > prod.product_name.virtual_available:
						warn_msg = _('You plan to sell %s but you have only  %s quantities of the product %s available, and the total quantity to sell is  %s !!'%(self.quantity, prod.product_name.virtual_available, prod.product_name.name, self.quantity * prod.product_quantity)) 
						return {
					    'warning': {
					        'title': 'Invalid value',
					        'message': warn_msg
					    }
					}



 
