from odoo import api, fields, models, tools, _
import json
from odoo.tools import float_is_zero
import logging
logger = logging.getLogger(__name__)
from datetime import datetime


class PosOrder(models.Model):
    _inherit = "pos.order"

    def create_picking(self):
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id
            if picking_type:
                message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                picking_vals = {
                    'origin': order.name,
                    'partner_id': address.get('delivery', False),
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }
                pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if pos_qty:
                    order_picking = Picking.create(picking_vals.copy())
                    order_picking.message_post(body=message)
                neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if neg_qty:
                    return_vals = picking_vals.copy()
                    return_vals.update({
                        'location_id': destination_id,
                        'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        'picking_type_id': return_pick_type.id
                    })
                    return_picking = Picking.create(return_vals)
                    return_picking.message_post(body=message)
            for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_digits=l.product_id.uom_id.rounding)):
                bom = self.env['mrp.bom'].search([('product_id','=',line.product_id.id)])
                if not bom:
                    moves |= Move.create({
                        'name': line.name,
                        'product_uom': line.product_id.uom_id.id,
                        'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                        'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': abs(line.qty),
                        'state': 'draft',
                        'location_id': location_id if line.qty >= 0 else destination_id,
                        'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                    })
                    if moves and not return_picking and not order_picking:
                        tracked_moves = moves.filtered(lambda move: move.product_id.tracking != 'none')
                        untracked_moves = moves - tracked_moves
                        tracked_moves.action_confirm()
                        untracked_moves.action_assign()
                        moves.filtered(lambda m: m.state in ['confirmed', 'waiting']).force_assign()
                        moves.filtered(lambda m: m.product_id.tracking == 'none').action_done()

            # prefer associating the regular order picking, not the return
            order.write({'picking_id': order_picking.id or return_picking.id})
            if return_picking:
                order._force_picking_done(return_picking)
            if order_picking:
                order._force_picking_done(order_picking)

            # when the pos.config has no picking_type_id set only the moves will be created
        return True

    @api.multi
    def reduce_bom_stock(self, order_line):
        order_line = json.loads(order_line)
        if order_line.get('state',False) != 'Done':
            qty = order_line.get('qty')
            bom_obj = self.env['mrp.bom']
            pos_config_ids = order_line.get('session_info').get('created').get('pos').get('id')
            pos_id = order_line.get('id', False)
            pos_order_id = self.env['pos.order'].browse(pos_id)
            pos_config_id = self.env['pos.config'].browse(pos_config_ids)
            bom = bom_obj.search([('product_id','=',order_line.get('product_id'))])
            for line in bom.bom_line_ids:
                inner_bom = bom_obj.search([('product_id', '=', line.product_id.id)])
                if not inner_bom:
                    amount = line.product_uom_id._compute_quantity(float(float(line.product_qty) * float(qty)), line.product_id.uom_id, round=True, rounding_method='UP')
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
                    for inner_line in inner_bom.bom_line_ids:
                        amount = inner_line.product_uom_id._compute_quantity(float(float(line.product_qty) * float(inner_line.product_qty) * float(qty)), inner_line.product_id.uom_id, round=True, rounding_method='UP')
                        move = self.env['stock.move'].create({
                            'name': 'POS',
                            'date': datetime.now(),
                            'date_expected': datetime.now(),
                            'product_id': inner_line.product_id.id,
                            'product_uom': inner_line.product_id.uom_id.id,
                            'product_uom_qty': float(amount),
                            'location_id': pos_config_id.stock_location_id.id,
                            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                            'company_id': pos_config_id.company_id.id,
                            'origin': 'POS',
                        })
                        move.action_confirm()
                        move.action_done()
        return order_line
