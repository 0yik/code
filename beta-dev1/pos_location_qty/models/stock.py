# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def disp_prod_stock(self, product_id, shop_id):
        stock_line = []

        total_qty = 0
        shop_qty = 0
        quant_obj = self.env['stock.quant']
        for warehouse_id in self.search([]):
            ware_record = warehouse_id
            location_id = ware_record.lot_stock_id.id
            if shop_id:
                loc_ids1 = self.env['stock.location'].search([('location_id','child_of',[shop_id])])
                stock_quant_ids1 = quant_obj.search([('location_id','in',[loc_id.id for loc_id in loc_ids1]), ('product_id', '=', product_id)])
                for stock_quant_id1 in stock_quant_ids1:
                    shop_qty = stock_quant_id1.qty
            loc_ids = self.env['stock.location'].search([('location_id','child_of',[location_id])])
            pruduct_ware_qty = 0.0
            location_line = []
            for loc_id in loc_ids:
                product_qty = 0.0
                stock_quant_ids = quant_obj.search([('location_id','in',[loc_id.id]), ('product_id', '=', product_id)])
                for stock_quant_id in stock_quant_ids:
                    product_qty += stock_quant_id.qty
                location_line.append([loc_id.name, product_qty])
                pruduct_ware_qty += product_qty
            stock_line.append([ware_record.name, pruduct_ware_qty, location_line])
            total_qty += pruduct_ware_qty
        return stock_line, total_qty, shop_qty

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
