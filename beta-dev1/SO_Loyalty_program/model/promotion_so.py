# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp

class res_partner(models.Model):
	_inherit = 'res.partner'

	cus_birthday = fields.Date('Birthday')

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	gift_order_line = fields.One2many('gift.order.line', 'order_id','Gift Order')
	use_promo = fields.Boolean('Promotion Program', default=False)
	pos_promotion_selected_ids = fields.Many2many('pos.promotion', 'selected_promotion_rel','order_id', 'promotion_id',string='Promotion Program')
	# @api.multi
	# def action_confirm(self):
	# 	# promotional_product_id = self.env.ref('so_promotion.promotion_service_01')
	# 	has_promotion = False
	# 	for line in self.order_line:
	# 		if line.product_id.default_code == 'PS':
	# 			has_promotion = True
	# 			break
	# 	if not has_promotion:
	# 		raise UserError(_('Warning! You need apply promotion first'))
	# 	return super(SaleOrder, self).action_confirm()

class GiftOrderLine(models.Model):
    _name = 'gift.order.line'
    
    order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)        
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description')
    product_uom_qty = fields.Float(string='Quantity', default=1.0)	
    product_uom = fields.Many2one('product.uom', string='Unit of Measure')
    price_unit = fields.Float('Unit Price', default=0.0)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    discount = fields.Float(string='Discount (%)', default=0.0)
    price_subtotal = fields.Float(string='Subtotal')
    price_total = fields.Float(string='Total')
    
class pos_promotion(models.Model):
	_inherit = 'pos.promotion'
	
	apply_so = fields.Boolean('Apply on Sales Order')
	to_valid = fields.Boolean('Valid For so')
	item_type = fields.Selection([('all item no exception','All Item No Exception'),
										('all item with exception','All Item With Exception'),
										('must include specific item','Must Include Specific Item'),
										('specific item only','Specific Item Only')
										], string='Item Type', help='1. All item No Exception : Promo will apply to all item without exception, you don`t have to enter any item.\n 2.All item with Exception : Promo will apply to all item except item listed here, please select exceptional item from the list. \n 3.Must Include Specific Item : Promo will apply if included specific item listed here, please select functional from list. \n 4.Specific Item Only : Promo will apply only to specific item listed here, please select functional item from the list',default='all item no exception')
    
	@api.model
	def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
		if self._context and 'from_so_search' in self._context:
			active_id = self._context.get('from_so_search')
			sale_obj = self.env['sale.order'].browse(active_id)
			promotions = self.env['pos.promotion'].search([])
			final_promotion = []
			for promo in promotions:
				if promo.period_type == 'all_time':
					final_promotion.append(promo.id)
				elif promo.period_type == 'birthday' and sale_obj.partner_id.cus_birthday == date.today().strftime('%Y-%m-%d'):
					final_promotion.append(promo.id)
				elif promo.period_type == 'certain_time' and sale_obj.date_order >= promo.start_date and sale_obj.date_order <= promo.end_date:
					final_promotion.append(promo.id)
			if final_promotion:
				domain.append(('id', 'in', final_promotion))
		return super(pos_promotion, self).search_read(domain=domain, fields=fields, offset=offset,limit=limit, order=order)
