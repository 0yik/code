# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import json


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    next_view_id = fields.Many2one('stock.pack.operation', 'Next View ID')
    check_close = fields.Boolean('Close')

    @api.model
    def create(self, vals):
        vals.update({
            'check_close' : False,
            'next_view_id' : False,
        })
        res = super(StockPackOperation, self).create(vals)
        res.update_qty_done()
        return res

    @api.multi
    def write(self, vals):
        vals.update({
            'check_close': False,
            'next_view_id': False,
        })
        res = super(StockPackOperation, self).write(vals)
        for record in self:
            record.update_qty_done()
        return res

    @api.model
    def update_qty_done(self):
        qty_done = sum([x.qty for x in self.pack_lot_ids])
        self._cr.execute(
            """
            UPDATE stock_pack_operation
            SET qty_done= %s 
            WHERE id= %s
            """%(qty_done, self.id)
        )

    ######## inhrit existed stock funtion to add default_picking_id##########
    @api.multi
    def action_split_lots(self):
        action_ctx = dict(self.env.context)
        action_ctx['default_picking_id'] = self.picking_id.id or False

        # If it's a returned stock move, we do not want to create a lot
        returned_move = self.linked_move_operation_ids.mapped('move_id').mapped('origin_returned_move_id')
        picking_type = self.picking_id.picking_type_id
        action_ctx.update({
            'serial': self.product_id.tracking == 'serial',
            'only_create': picking_type.use_create_lots and not picking_type.use_existing_lots and not returned_move,
            'create_lots': picking_type.use_create_lots,
            'state_done': self.picking_id.state == 'done',
            'show_reserved': any([lot for lot in self.pack_lot_ids if lot.qty_todo > 0.0])})
        view_id = self.env.ref('stock.view_pack_operation_lot_form').id
        return {
            'name': _('Lot/Serial Number Details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.pack.operation',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx}
    split_lot = action_split_lots

    ######### END ##########

    def on_barcode_scanned(self, barcode):
        if barcode:
            Product = self.env['product.product']
            Picking = self.env['stock.picking']
            Picking_Line = self.env['stock.pack.operation']
            correct_product = Product.search(
                [('id', '!=', self.product_id.id), '|', ('barcode', '=', barcode), ('default_code', '=', barcode)])
            if correct_product:
                if self._context.get('default_picking_id', False):
                    picking_id = Picking.browse(self._context.get('default_picking_id'))
                    if picking_id and picking_id.id and picking_id.picking_type_id.name in ['Receipts',
                                                                                            'Delivery Orders',
                                                                                            'Internal Transfers']:
                        pack_vals = {
                            'picking_id': picking_id.id,
                            'product_id': correct_product.id,
                            'product_uom_id': correct_product.uom_id.id,
                            'product_qty': 1,
                            'qty_done': 0,
                            'location_id': picking_id.location_id.id,
                            'location_dest_id': picking_id.location_dest_id.id,
                            'date': fields.Datetime.now(),
                        }
                        new_line = Picking_Line.create(pack_vals)
                        if correct_product.tracking in ['serial', 'lot'] and new_line:
                            return {'value': {'next_view_id': new_line.id}}
                        else:
                            return {'value': {'check_close': True}}
        res = super(StockPackOperation, self).on_barcode_scanned(barcode)
        return res

class stock_pack_operation_lot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    @api.model
    def create(self, vals):
        res = super(stock_pack_operation_lot, self).create(vals)
        if res.operation_id:
            res.operation_id.update_qty_done()
        return res

    @api.multi
    def write(self, vals):
        res = super(stock_pack_operation_lot, self).write(vals)
        for record in self:
            if record.operation_id:
                record.operation_id.update_qty_done()
        return res
