import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.exceptions import Warning
from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    own_wh_qty = fields.Float(string='Qty on My Warehouse',compute='_get_own_warehouse_quantity')
    # ir_forcast_qty = fields.Float(string='IR Forecast Qty',compute='_get_ir_forecast_quantity')

    def _get_own_warehouse_quantity(self):
        user_obj = self.env['res.users']
        quant_obj = self.env['stock.quant']
        branch = self.env.user.branch_id
        warehouse = branch.warehouse_id
        if warehouse:
            location_ids = self.env['stock.location'].search([('location_id','=',warehouse.view_location_id.id)])
            if location_ids:
                for product in self:
                    quants = quant_obj.search([('product_id','=',product.id),('location_id','in',[location_ids.id])])
                    for q in quants:
                        product.own_wh_qty += q.qty

    # def _get_ir_forecast_quantity(self):
    #     for product in self:
    #         requested_ids = self.env['inventory.request.line'].search([('product_id','=',product.id)])
    #         if requested_ids:
    #             for q in requested_ids:
    #                 picking_ids = ''
    #                 print "DDDDDDDDDDDD0", q.inventory_request_id.state
    #                 if q.inventory_request_id:
    #                     picking_ids = self.env['stock.picking'].search([('inventory_request_id','=',q.inventory_request_id.id),('state','=','done')])
    #                 if not picking_ids and q.inventory_request_id.state == 'approved':
    #                     product.ir_forcast_qty += float(q.product_qty)

