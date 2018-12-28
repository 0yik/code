# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import  api, fields, models, tools, _
from odoo.exceptions import UserError, Warning, RedirectWarning

class PosConfig(models.Model):
	_inherit = 'pos.config'
	related_stock_location_ids = fields.Many2many('stock.location', 'pos_config_stock_location_rel', 'pos_config_id', 'stock_location_id', string='Other Related Stock Locations',)

class ProductProduct(models.Model):
	_inherit = 'product.product'

	@api.model
	def get_product_stock_info(self,stock_info):
		result = {}
		stock_status = False
		for location_id in stock_info['location_ids']:
			product_obj = self.with_context({'pricelist':stock_info['pricelist_id'], 'display_default_code': False ,'location':location_id})
			if (stock_info['stock_type'] == 'available_qty'):
				product_qty = product_obj.browse(stock_info['product_id']).qty_available
			elif (stock_info['stock_type'] == 'forecasted_qty'):
				product_qty = product_obj.browse(stock_info['product_id']).virtual_available
			else:
				product_qty = product_obj.browse(stock_info['product_id']).qty_available - product_obj.browse(stock_info['product_id']).outgoing_qty
			if(product_qty > 0):
				stock_status = True
			stock_name = self.env['stock.location'].browse(location_id).display_name
			result[location_id] = [product_qty,location_id,stock_name]
		if stock_status:
			return result
		else:
			return False

class PosOrderLine(models.Model):
	_inherit = 'pos.order.line'
	
	stock_location_id = fields.Many2one('stock.location',string="Stock Location")
	
	@api.model
	def _order_line_fields(self,line):
		fields_return = super(PosOrderLine,self)._order_line_fields(line)
		fields_return[2].update({'stock_location_id':line[2].get('stock_location_id','')})
		return fields_return

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	pos_order_id = fields.Many2one('pos.order',string="POS Order")


	@api.model
	def enable_multi_stock_locations(self):
		stock_config_setting_obj = self.env['stock.config.settings'].create({
			'warehouse_and_location_usage_level':2
		})
		stock_config_setting_obj.group_stock_multi_locations = stock_config_setting_obj.warehouse_and_location_usage_level > 0
		stock_config_setting_obj.group_stock_multi_warehouses = stock_config_setting_obj.warehouse_and_location_usage_level > 1
		stock_config_setting_obj.execute()


class PosOrder(models.Model):
	_inherit = 'pos.order'

	related_picking_id = fields.One2many('stock.picking','pos_order_id',readonly=True,string="Related Pickings")

	def create_picking(self):		
		"""Create a picking for each order and validate it."""
		Picking = self.env['stock.picking']
		Move = self.env['stock.move']
		StockWarehouse = self.env['stock.warehouse']
		for order in self:
			
			address = order.partner_id.address_get(['delivery']) or {}
			picking_type = order.picking_type_id
			picking_id = False
			location_id = order.location_id.id
			if order.partner_id:
				destination_id = order.partner_id.property_stock_customer.id
			else:
				if (not picking_type) or (not picking_type.default_location_dest_id):
					customerloc, supplierloc = StockWarehouse._get_partner_locations()
					destination_id = customerloc.id
				else:
					destination_id = picking_type.default_location_dest_id.id
			stock_location_ids = []
#---------------------------------- code for POS Warehouse Management ------------------------------------------
			for line in order.lines.filtered(lambda l: l.stock_location_id):
				stock_location_ids.append(line.stock_location_id.id)
			if picking_type and len(stock_location_ids) != len(order.lines.ids):
				pos_qty = all([x.qty >= 0 for x in order.lines])
				picking_id = Picking.create({
					'origin': order.name,
					'partner_id': address.get('delivery', False),
					'date_done': order.date_order,
					'picking_type_id': picking_type.id,
					'company_id': order.company_id.id,
					'move_type': 'direct',
					'note': order.note or "",
					'location_id': location_id if pos_qty else destination_id,
					'location_dest_id': destination_id if pos_qty else location_id,
				})
				message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
				picking_id.message_post(body=message)
				order.write({'picking_id': picking_id.id})

				for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not l.stock_location_id):
					Move += Move.create({
						'name': line.name,
						'product_uom': line.product_id.uom_id.id,
						'picking_id': picking_id and picking_id.id or False,
						'picking_type_id': picking_type.id,
						'product_id': line.product_id.id,
						'product_uom_qty': abs(line.qty),
						'state': 'draft',
						'location_id': location_id if line.qty >= 0 else destination_id,
						'location_dest_id': destination_id if line.qty >= 0 else location_id,
					})
		
			stock_location_ids = list(set(stock_location_ids))
			
			for stock_location_id in stock_location_ids:
				loc_picking_id = False
				move_obj = self.env['stock.move']
				loc_picking_id = Picking.create({
					'pos_order_id':order.id,
					'origin': order.name,
					'partner_id': address.get('delivery', False),
					'date_done': order.date_order,
					'picking_type_id': picking_type.id,
					'company_id': order.company_id.id,
					'move_type': 'direct',
					'note': order.note or "",
					'location_id': stock_location_id,
					'location_dest_id': destination_id,
				})
				for line in order.lines.filtered(lambda l: l.stock_location_id.id == stock_location_id ):
					move_obj += move_obj.create({
						'name': line.name,
						'product_uom': line.product_id.uom_id.id,
						'picking_id': loc_picking_id and loc_picking_id.id or False,
						'picking_type_id': picking_type.id,
						'product_id': line.product_id.id,
						'product_uom_qty': abs(line.qty),
						'state': 'draft',
						'location_id': stock_location_id ,
						'location_dest_id': destination_id ,
					})			
				if loc_picking_id:
					loc_picking_id.action_confirm()
					loc_picking_id.force_assign()

				elif move_obj:
					move_obj.action_confirm()
					move_obj.force_assign()
					move_obj.action_done()
#---------------------------------- code for POS Warehouse Management End -------------------------------------
			if picking_id:
				picking_id.action_confirm()
				picking_id.force_assign()
				order.set_pack_operation_lot()
				picking_id.action_done()
			elif Move:
				Move.action_confirm()
				Move.force_assign()
				Move.action_done()
		return True