# -*- coding: utf-8 -*-
import time
from odoo import models, api, _, fields
from odoo.exceptions import except_orm, UserError

class purchase_update(models.TransientModel):
    _name = 'purchase.update'
    _description = 'Sale Update'

    def _get_order(self):
        return self._context['active_id']

    def _get_order_lines(self):
        order_lines = []
        order = self.env['purchase.order'].browse(self._context['active_id'])
        for line in order.order_line:
            order_lines.append({
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.product_qty,
                'price_unit': line.price_unit,
                'sub_total': line.product_qty * line.price_unit,
                'order_line_id': line.id,
                'date_planned': line.date_planned
            })
        return order_lines

    @api.one
    @api.depends('order_lines', 'order_lines.quantity', 'order_lines.price_unit')
    def _total(self):
        total = 0
        for line in self.order_lines:
            total += line.quantity * line.price_unit
        self.amount_total = total

    purchase_id  = fields.Many2one('purchase.order', 'Purchase Order', default=_get_order)
    order_lines  = fields.One2many('purchase.update.line', 'purchase_id', 'Lines', default=_get_order_lines)
    amount_total = fields.Float('Total Amount', compute=_total)

    @api.one
    def action_update(self):
        order = self.purchase_id
        picking = self.purchase_id.picking_ids
        # stock_transfer = self.env['stock.transfer_details'].search([('picking_id', '=', picking.id)])
        version = self.env['purchase.version'].create({
            'name': order.name,
            'update_user_id': self.env.user.id,
            'update_date': time.strftime('%Y-%m-%d'),
            'purchase_id': order.id
        })
        for line in order.order_line:
            self.env['purchase.version.line'].create({
                'version_id': version.id,
                'product_id': line.product_id and line.product_id.id or False,
                'name': line.name,
                'quantity': line.product_qty,
                'price_unit': line.price_unit
            })

        rem_polines    = self.order_lines.mapped('order_line_id')
        lines_todelete = order.order_line - rem_polines
        mov_todelete   = lines_todelete.mapped('move_ids')
        lines_todelete.unlink()
        for m in mov_todelete:
            for pack in m.mapped('linked_move_operation_ids'):
                pack.operation_id.unlink()
        mov_todelete.unlink()

        for line in self.order_lines:
            if line.order_line_id:
                line.order_line_id.write({
                    'product_id': line.product_id and line.product_id.id or False,
                    'name': line.name,
                    'product_qty': line.quantity,
                    'price_unit': line.price_unit,
                    'date_planned': line.date_planned,
                })
                for move in picking.move_lines.filtered(lambda x : x.product_id == line.product_id):
                    if move.state not in ('cancle', 'done'):
                        values = {
                            'picking_id': picking.id,
                            'name': line.product_id.name,
                            'product_id': line.product_id and line.product_id.id or False,
                            'product_uom_qty': line.quantity,
                            'product_uos_qty': line.quantity,
                            'location_dest_id': move.location_dest_id.id if move.location_dest_id.id else picking.picking_type_id.default_location_dest_id.id,
                            'product_uom': line.product_id.uom_po_id.id,
                            'location_id': move.location_id.id if move.location_id.id else picking.picking_type_id.default_location_src_id.id,
                        }
                        move.write(values)
                        for op in picking.pack_operation_ids.filtered(lambda x : x.product_id == line.product_id):
                            op.write({'product_qty': line.quantity})
            else:
                purchase_line_id = self.env['purchase.order.line'].create({
                    'order_id': order.id,
                    'product_id': line.product_id and line.product_id.id or False ,
                    'name': line.name,
                    'product_qty': line.quantity,
                    'price_unit': line.price_unit,
                    'date_planned': line.date_planned,
                })
                values = {
                    'picking_id': picking.id,
                    'name': line.product_id.name,
                    'product_id': line.product_id and line.product_id.id or False ,
                    'product_uom_qty': line.quantity,
                    'location_dest_id': order.location_id.id,
                    'product_uom': line.product_id.uom_po_id.id,
                    'state': 'assigned',
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'origin': picking.origin,
                    'group_id': picking.group_id.id,
                    'picking_type_id': picking.picking_type_id.id,
                    'product_uos_qty': line.quantity,
                    'purchase_line_id': purchase_line_id.id,
                    'procurement_id': False,
                    'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
                    'warehouse_id': order.picking_type_id.warehouse_id.id,
                    'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
                }
                self.env['stock.move'].create(values)
                trans_value = {
                    'picking_id': picking.id,
                    'location_dest_id': order.location_id.id,
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'product_qty': line.quantity,
                    'product_uom_id': line.product_id.uom_po_id.id,
                    'product_id': line.product_id and line.product_id.id or False ,
                }
                self.env['stock.pack.operation'].create(trans_value)

        new_version = order.version_no + 1
        order.version_no = new_version
        order.name = order.name.split('(')[0] + '(' + str(new_version) + ')'
        return {'type': 'ir.actions.act_window_close'}

class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def unlink(self):
        for move in self:
            picking = move.picking_id
            cont = {
                'picking': picking.id,
                'is_delete': True,
                'active_ids': [picking.id],
                'active_id': picking.id,
                'move_id': move.id,
                'move_qty': move.product_uom_qty,
            }
            if picking.state == 'done':
                wiz_obj = self.env.get('stock.return.picking')
                wiz_rec = wiz_obj.with_context(cont).create({})
                wiz_rec._create_returns()
            else:
                move.write({'state': 'cancel'})
            if move.state not in ('draft', 'cancel'):
                raise except_orm(_('User Error!'), _('You can only delete draft moves.'))

        return super(stock_move, self).unlink()

class stock_return_picking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError("You may only return one picking at a time!")
        res = super(stock_return_picking, self).default_get(fields)

        Quant = self.env['stock.quant']
        move_dest_exists = False
        product_return_moves = []
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if picking:
            if picking.state != 'done':
                raise UserError(_("You may only return Done pickings"))
            for move in picking.move_lines:
                if move.scrapped:
                    continue
                if move.move_dest_id:
                    move_dest_exists = True
                # Sum the quants in that location that can be returned (they should have been moved by the moves that were included in the returned picking)
                quantity = sum(quant.qty for quant in Quant.search([
                    ('history_ids', 'in', move.id),
                    ('qty', '>', 0.0), ('location_id', 'child_of', move.location_dest_id.id)
                ]).filtered(
                    lambda quant: not quant.reservation_id or quant.reservation_id.origin_returned_move_id != move
                ))
                quantity = move.product_id.uom_id._compute_quantity(quantity, move.product_uom)
                product_return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': quantity, 'move_id': move.id}))

                if not product_return_moves:
                    raise UserError(_('No products to return (only lines in Done state and not fully returned yet can be returned)!'))
                if 'product_return_moves' in fields:
                    res.update({'product_return_moves': product_return_moves})
                if 'move_dest_exists' in fields:
                    res.update({'move_dest_exists': move_dest_exists})
                if 'parent_location_id' in fields and picking.location_id.usage == 'internal':
                    res.update({'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
                if 'original_location_id' in fields:
                    res.update({'original_location_id': picking.location_id.id})
                if 'location_id' in fields:
                    location_id = picking.location_id.id
                    if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                        location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
                    res['location_id'] = location_id
        return res


class purchase_update_line(models.TransientModel):
    _name = 'purchase.update.line'
    _description = 'Sale Update Lines'

    @api.one
    @api.depends('price_unit', 'quantity')
    def _subtotal(self):
        self.sub_total = self.quantity * self.price_unit

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.name = self.product_id.name

    purchase_id   = fields.Many2one('purchase.update', 'Invoice')
    order_line_id = fields.Many2one('purchase.order.line', 'Purchase Line')
    product_id    = fields.Many2one('product.product', 'Product')
    name          = fields.Char('Description')
    quantity      = fields.Float('Quantity')
    price_unit    = fields.Float('Unit Price')
    sub_total     = fields.Float('Amount', compute=_subtotal)
    date_planned  = fields.Date('Scheduled Date', required=True, select=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
