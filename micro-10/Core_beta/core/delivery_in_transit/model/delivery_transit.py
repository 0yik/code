from odoo import api, fields, models,_
from openpyxl import Workbook
import tempfile
import base64
import binascii
import xlrd
import os
import logging
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)

class stock_location(models.Model):
    _inherit = "stock.location"
    
    usage = fields.Selection(selection_add=[('virtual_location', 'Virtual Location')]) 
    
class stock_pack_operation(models.Model):
    _inherit = 'stock.pack.operation'
    
    transit_quantity = fields.Float('Transit Quantity')

# class stock_move(models.Model):
#     _inherit = 'stock.move'
#
#     @api.multi
#     def write(self,vals):
#
#         return super(stock_move, self).write(vals)

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    state = fields.Selection([
        ('draft', 'Draft'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),('in_transit', 'In Transit'), ('done', 'Done')], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")
    
    @api.multi  
    def transit_order_transfer(self):
        stock_move_vals={}
        stock_vals = {}
        stock_transit_location = self.env['stock.location'].search([('name','=','Transiting Location'),('usage','=','virtual_location')])
        if stock_transit_location:
            pack_operation_product_ids = self.pack_operation_product_ids
            for pack_operation_id in pack_operation_product_ids:
                picking_id = pack_operation_id.picking_id       #stock_picking id
                transit_quantity = pack_operation_id.transit_quantity
                product_qty = pack_operation_id.product_qty
                if transit_quantity == 0.0:
                    view = self.env.ref('delivery_in_transit.view_transit_immediate_transfer')
                    wiz = self.env['stock.transit.immediate.transfer'].create({'pick_id': picking_id.id})
                    # TDE FIXME: a return in a loop, what a good idea. Really.
                    return {
                        'name': _('Immediate Transfer?'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.transit.immediate.transfer',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': self.env.context,
                    }
#                 if picking_id.check_backorder():
#                     view = self.env.ref('stock.view_backorder_confirmation')
#                     wiz = self.env['stock.backorder.confirmation'].create({'pick_id': picking_id.id})
#                     # TDE FIXME: same reamrk as above actually
#                     return {
#                         'name': _('Create Backorder?'),
#                         'type': 'ir.actions.act_window',
#                         'view_type': 'form',
#                         'view_mode': 'form',
#                         'res_model': 'stock.backorder.confirmation',
#                         'views': [(view.id, 'form')],
#                         'view_id': view.id,
#                         'target': 'new',
#                         'res_id': wiz.id,
#                         'context': self.env.context,
#                     }
#                 if transit_quantity < product_qty or  transit_quantity > product_qty:
#                     raise UserError(_('Transit Quantity should be equal to To-Do Quantity'))
                stock_move_obj = self.env['stock.move']
                stock_move_id = stock_move_obj.search([('picking_id','=',picking_id.id),('product_id','=',pack_operation_id.product_id.id)])
                 
                if stock_move_id:
#                     stock_move_vals['product_uom_qty'] = pack_operation_id.transit_quantity
                    stock_move_vals['location_dest_id'] = stock_transit_location.id
#                     stock_move_vals['name'] = pack_operation_id.product_id.name
#                     stock_move_vals['picking_type_id'] = picking_id.picking_type_id.id
                    stock_move_vals['location_id'] = pack_operation_id.location_id.id
#                     stock_move_vals['create_date'] = picking_id.min_date
#                     stock_move_vals['picking_partner_id'] = picking_id.partner_id.id
#                     stock_move_vals['priority'] = '1'
#                     stock_move_vals['product_id'] = pack_operation_id.product_id.id
#                     stock_move_vals['picking_id'] = picking_id.id
#                     stock_move_vals['picking_id'] = picking_id.id
#                     stock_move_vals['product_uom'] = pack_operation_id.product_uom_id.id
#                     stock_move_obj.create(stock_move_vals)
                    stock_move_id.write(stock_move_vals)
#                 res.action_confirm()
                stock_vals['state'] = 'in_transit'
                picking_id.write(stock_vals)
                    
    @api.multi
    def do_new_transfer(self):
        vals = {}

        for pick in self:
            if pick.state == 'done':
                raise UserError(_('The pick is already validated'))
            pack_operations_delete = self.env['stock.pack.operation']
            if not pick.move_lines and not pick.pack_operation_ids:
                raise UserError(_('Please create some Initial Demand or Mark as Todo and create some Operations. '))
            # In draft or with no pack operations edited yet, ask if we can just do everything
            if pick.state == 'draft' or all([x.qty_done == 0.0 for x in pick.pack_operation_ids]):
                # If no lots when needed, raise error
                picking_type = pick.picking_type_id
                if (picking_type.use_create_lots or picking_type.use_existing_lots):
                    for pack in pick.pack_operation_ids:
                        if pack.product_id and pack.product_id.tracking != 'none':
                            raise UserError(_('Some products require lots/serial numbers, so you need to specify those first!'))
                view = self.env.ref('stock.view_immediate_transfer')
                wiz = self.env['stock.immediate.transfer'].create({'pick_id': pick.id})
                # TDE FIXME: a return in a loop, what a good idea. Really.
                return {
                    'name': _('Immediate Transfer?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.immediate.transfer',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }

            # Check backorder should check for other barcodes
            if pick.check_backorder():
                view = self.env.ref('stock.view_backorder_confirmation')
                wiz = self.env['stock.backorder.confirmation'].create({'pick_id': pick.id})
                # TDE FIXME: same reamrk as above actually
                return {
                    'name': _('Create Backorder?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.backorder.confirmation',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }
            for operation in pick.pack_operation_ids:
                if operation.qty_done < 0:
                    raise UserError(_('No negative quantities allowed'))
                if operation.qty_done > 0:
                    operation.write({'product_qty': operation.qty_done})
                else:
                    pack_operations_delete |= operation
            if pack_operations_delete:
                pack_operations_delete.unlink()
        self.do_transfer()

        for pack_operation_id in self.pack_operation_product_ids:
            vals[pack_operation_id.product_id.id] = pack_operation_id.location_dest_id.id
        move_lines = self.move_lines



        for move_line in move_lines:
            location_dest_id = move_line.location_dest_id
            location_id = move_line.location_id
            product_id = move_line.product_id.id
            sql_query = """select * from stock_move where id = %s"""
            params = (move_line.id,)
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.dictfetchall()
            move_vals = results[0]
            move_vals.pop('product_qty')
            move_vals.update({'state':'assigned','location_id':location_dest_id.id , 'location_dest_id':vals.get(product_id)})
            res = self.env['stock.move'].create(move_vals)
            res.sudo().write({'state':'done'})
#             move_line.sudo().write({'state':'assigned'})
#             move_line.sudo().write({'location_id':location_dest_id.id , 'location_dest_id':vals.get(product_id)})
#             move_line.sudo().write({'state':'done'})
        return

    @api.multi
    def do_transfer(self):
        """ If no pack operation, we do simple action_done of the picking.
        Otherwise, do the pack operations. """
        # TDE CLEAN ME: reclean me, please
        self._create_lots_for_picking()

        no_pack_op_pickings = self.filtered(lambda picking: not picking.pack_operation_ids)
        no_pack_op_pickings.action_done()
        other_pickings = self - no_pack_op_pickings
        for picking in other_pickings:
            need_rereserve, all_op_processed = picking.picking_recompute_remaining_quantities()
            todo_moves = self.env['stock.move']
            todo_moves_old = self.env['stock.move']
            toassign_moves = self.env['stock.move']

            # create extra moves in the picking (unexpected product moves coming from pack operations)
            if not all_op_processed:
                todo_moves |= picking._create_extra_moves()

            if need_rereserve or not all_op_processed:
                moves_reassign = any(x.origin_returned_move_id or x.move_orig_ids for x in picking.move_lines if
                                     x.state not in ['done', 'cancel'])
                if moves_reassign and picking.location_id.usage not in ("supplier", "production", "inventory"):
                    # unnecessary to assign other quants than those involved with pack operations as they will be unreserved anyways.
                    picking.with_context(reserve_only_ops=True, no_state_change=True).rereserve_quants(
                        move_ids=picking.move_lines.ids)
                picking.do_recompute_remaining_quantities()
            stock_transit_location = self.env['stock.location'].search(
                [('name', '=', 'Transiting Location'), ('usage', '=', 'virtual_location')])
            # split move lines if needed
            for move in picking.move_lines:
                rounding = move.product_id.uom_id.rounding
                remaining_qty = move.remaining_qty
                if move.state in ('done', 'cancel'):
                    # ignore stock moves cancelled or already done
                    continue
                elif move.state == 'draft':
                    toassign_moves |= move
                if float_compare(remaining_qty, 0, precision_rounding=rounding) == 0:
                    if move.state in ('draft', 'assigned', 'confirmed'):
                        todo_moves |= move
                        todo_moves_old = todo_moves
                        todo_moves = self.env['stock.move']
                        for todo_move in todo_moves_old:
                            todo_moves |= todo_move.copy()
                elif float_compare(remaining_qty, 0, precision_rounding=rounding) > 0 and float_compare(remaining_qty,
                                                                                                        move.product_qty,
                                                                                                        precision_rounding=rounding) < 0:
                    # TDE FIXME: shoudl probably return a move - check for no track key, by the way
                    new_move_id = move.split(remaining_qty)
                    new_move = self.env['stock.move'].with_context(mail_notrack=True).browse(new_move_id)
                    todo_moves |= move
                    # Assign move as it was assigned before
                    toassign_moves |= new_move

            for todo_move in todo_moves_old:
                todo_move.write(
                {'location_id': stock_transit_location.id, 'location_dest_id': todo_move.picking_id.location_dest_id.id})
            # TDE FIXME: do_only_split does not seem used anymore
            if todo_moves and not self.env.context.get('do_only_split'):
                todo_moves.action_done()
            elif self.env.context.get('do_only_split'):
                picking = picking.with_context(split=todo_moves.ids)
            picking._create_backorder()
            # changing the location when state is on In transit to done
            if todo_moves_old:
                todo_moves_old.write({'picking_id':False,'origin':todo_moves.picking_id.name})
        return True