# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError
import json
from datetime import datetime


class BomLineImage(models.Model):
    _inherit = 'mrp.bom.line'

    mrp_efficiency = fields.Float('Efficiency')

class PosOrder(models.Model):
    _inherit = "pos.order"

   
    @api.multi
    def reduce_bom_stock(self, order_line):
        def check_bom(bom, qty):
            bom_obj = self.env['mrp.bom']
            for line in bom.bom_line_ids:
                inner_bom = bom_obj.search([('product_id', '=', line.product_id.id)])
                if not inner_bom:
                    amount = line.product_uom_id._compute_quantity(float(float(line.product_qty) * float(qty)), line.product_id.uom_id, round=True, rounding_method='UP')
                    if line.mrp_efficiency:
                    	amount = 100 * amount / line.mrp_efficiency
                    move = self.env['stock.move'].create({
                        'name': 'POS',
                        'date': datetime.now(),
                        'date_expected': datetime.now(),
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_id.id,
                        'product_uom_qty': float(amount),
                        'location_id': pos_config_id.stock_location_id.id,
                        'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                        'company_id': pos_config_id.company_id.id,
                        'origin': 'POS',
                    })
                    move.action_confirm()
                    move.action_done()
                else:
                    qty = line.product_uom_id._compute_quantity(float(float(line.product_qty) * float(qty)), line.product_id.uom_id, round=True, rounding_method='UP')
                    check_bom(inner_bom, qty)
            return

        order_line = json.loads(order_line)
        if order_line.get('state',False) != 'Done':
            
            qty = order_line.get('qty')
            bom_obj = self.env['mrp.bom']
            pos_id = order_line.get('id', False)
            pos_order_id = self.env['pos.order'].browse(pos_id)
            pos_config_id = self.env['pos.session'].browse(order_line.get('pos_session_id')).config_id
            bom = bom_obj.search([('product_id','=',order_line.get('product_id'))])
            check_bom(bom, qty)
        return order_line