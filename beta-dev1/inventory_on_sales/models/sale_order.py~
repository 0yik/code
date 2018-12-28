from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	standard_qty_shop = fields.Char(string='Stock Display Shop', readonly=True)
	current_qty_shop = fields.Char(string='Stock Current Shop', readonly=True)
	standard_qty_warehouse = fields.Char(string='Stock Display Warehouse', readonly=True)
	current_qty_warehouse = fields.Char(string='Stock Current Warehouse', readonly=True)
	location_id = fields.Many2one('stock.location', string='Shop')
	warehouse_id = fields.Many2one('stock.location', string='Warehouse')
	
	@api.multi
	@api.onchange('product_id')
	def product_id_change(self):
		#is_shop standard_qty_shop_value
		warehouse_orderpoint_is_shop = self.product_id.orderpoint_ids.filtered(lambda a: a.location_id.is_shop == True)
		is_shop_list = warehouse_orderpoint_is_shop.mapped('id')
		standard_qty_shop_value = warehouse_orderpoint_is_shop.search([('id', 'in', is_shop_list)], limit=1, order='id desc')
		#is_not_shop standard_qty_warehouse
		warehouse_orderpoint_is_not_shop = self.product_id.orderpoint_ids.filtered(lambda a: a.location_id.is_shop != True)
		is_not_shop_list = warehouse_orderpoint_is_not_shop.mapped('id')
		standard_qty_warehouse_value = warehouse_orderpoint_is_not_shop.search([('id', 'in', is_not_shop_list)], limit=1, order='id desc')

		stock_quant_records = self.env['stock.quant'].search([('product_id', '=', self.product_id.id)])
		current_qty_store = sum(stock_quant_records.filtered(lambda a:a.location_id.is_shop == True).mapped('qty'))

		self.standard_qty_shop = standard_qty_shop_value.product_min_qty
		self.current_qty_shop = current_qty_store
		self.standard_qty_warehouse = standard_qty_warehouse_value.product_min_qty
		self.current_qty_warehouse = self.product_id.qty_available
		return super(SaleOrderLine,self).product_id_change()
	
	#Location onchange
	@api.multi
	@api.onchange('location_id')
	def location_id_change(self):
		standard_qty_shop_value =self.env['stock.warehouse.orderpoint'].search([('location_id', '=', self.location_id.id)], limit=1, order='id desc')
		stock_quant_records = self.env['stock.quant'].search([('product_id', '=', self.product_id.id), ('location_id', '=', self.location_id.id)])
		current_qty_store = 0
		if stock_quant_records:
			current_qty_store = sum(stock_quant_records.mapped('qty'))
		print "current_qty_store===>>>",current_qty_store
		print "standard_qty_shop_value=======>>>>",standard_qty_shop_value
		print "standard_qty_shop_value.product_min_qty=======>>>>",standard_qty_shop_value.product_min_qty
		self.standard_qty_shop = standard_qty_shop_value.product_min_qty
		self.current_qty_shop = current_qty_store
		
		return 

	#Warehouse onchange (which location is_not_shop)
	@api.multi
	@api.onchange('warehouse_id')
	def warehouse_id_change(self):
		
		standard_qty_warehouse_value =self.env['stock.warehouse.orderpoint'].search([('location_id', '=', self.warehouse_id.id)], limit=1, order='id desc')
		print "standard_qty_warehouse_value=======>>>>",standard_qty_warehouse_value
		print "standard_qty_warehouse_value.product_min_qty=======>>>>",standard_qty_warehouse_value.product_min_qty
		stock_quant_records = self.env['stock.quant'].search([('product_id', '=', self.product_id.id), ('location_id', '=', self.warehouse_id.id)])
		current_qty_warehouse = 0
		if stock_quant_records:
			current_qty_warehouse = sum(stock_quant_records.mapped('qty'))
		self.standard_qty_warehouse = standard_qty_warehouse_value.product_min_qty
		self.current_qty_warehouse = current_qty_warehouse
		#self.current_qty_warehouse = self.product_id.qty_available
		
		return 
	

class SaleOrder(models.Model):
	_inherit = 'sale.order'
