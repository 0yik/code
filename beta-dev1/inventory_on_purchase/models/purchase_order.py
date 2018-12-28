from odoo import api, fields, models, _
from datetime import datetime, timedelta, date


class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	warehouse_id = fields.Many2one('stock.location', string='Warehouse')
	last_purchase_history = fields.Char(string='Last Purchase History', readonly=True)
	last_purchase_qty = fields.Char(string='Last Purchase Qty', readonly=True)
	stock_current_warehouse = fields.Char(string='Stock Current Warehouse', readonly=True)
	stock_display_warehouse = fields.Char(string='Stock Display Warehouse', readonly=True)
	has_purchase_request_lines = fields.Boolean(string="Has Purchase Request Lines")

	
	@api.multi
	@api.onchange('product_id')
	def onchange_product_id(self):
		last_product_order_line_record = self.env['purchase.order.line'].search([('product_id', '=', self.product_id.id)], limit=1, order='id desc')
		current_warehouse_current_product_qty = self.env['stock.quant'].search([('product_id', '=', self.product_id.id), ('location_id', '=', self.warehouse_id.id)])
		current_qty_warehouse = 0
		if current_warehouse_current_product_qty:
			current_qty_warehouse = sum(current_warehouse_current_product_qty.mapped('qty'))
		self.last_purchase_history = last_product_order_line_record.date_planned
		self.last_purchase_qty = last_product_order_line_record.product_qty
		#self.stock_display_warehouse = self.product_id.qty_available
		self.stock_current_warehouse = current_qty_warehouse
		if self.warehouse_id.id:
		    reordering_rules = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', self.product_id.id), ('location_id', '=', self.warehouse_id.id), ('location_type', '=', 'warehouse')], limit=1)
		    if reordering_rules:
		        self.stock_display_warehouse = reordering_rules.product_min_qty
		    else:
		        self.stock_display_warehouse = 0
		    
		return super(PurchaseOrderLine, self).onchange_product_id()

	@api.multi
	@api.onchange('warehouse_id')
	def warehouse_id_change(self):
		current_warehouse_current_product_qty = self.env['stock.quant'].search([('product_id', '=', self.product_id.id), ('location_id', '=', self.warehouse_id.id)])
		current_qty_warehouse = 0
		#print "current_warehouse_current_product_qty",current_warehouse_current_product_qty
		#print "before current_qty_warehouse====>>>>",current_qty_warehouse
		if current_warehouse_current_product_qty:
			current_qty_warehouse = sum(current_warehouse_current_product_qty.mapped('qty'))
		#print "after current_qty_warehouse===>>",current_qty_warehouse
		self.stock_current_warehouse = current_qty_warehouse
		reordering_rules = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', self.product_id.id), ('location_id', '=', self.warehouse_id.id), ('location_type', '=', 'warehouse')], limit=1)
		if reordering_rules:
		    self.stock_display_warehouse = reordering_rules.product_min_qty
		else:
		    self.stock_display_warehouse = 0
		return 

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	state = fields.Selection([
	('draft', 'RFQ'),
	('sent', 'RFQ Sent'),
	('to approve', 'To be Approved'),
	('purchase', 'Purchase Order'),
	('reject','Rejected'),
	('done', 'Locked'),
	('cancel', 'Cancelled')
	], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')


