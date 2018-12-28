# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

import time

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _compute_work_order(self):
        flag = 0
        for line in self:
            for move in line.move_lines:
                if move.product_id.type == 'service' or move.product_id.type == 'product':
                    flag = 1
            if flag == 1:
                line.is_work_order = True


    sale_order_id = fields.Many2one('sale.order', 'Sale Order Reference')
    is_work_order = fields.Boolean('Is A work order',compute='_compute_work_order' )

    @api.multi
    def _create_backorder(self, backorder_moves=[]):

        backorders = self.env['stock.picking']
        for picking in self:
            backorder_moves = backorder_moves or picking.move_lines
            if self._context.get('do_only_split'):
                not_done_bo_moves = backorder_moves.filtered(lambda move: move.id not in self._context.get('split', []))
            else:
                not_done_bo_moves = backorder_moves.filtered(lambda move: move.state not in ('done', 'cancel'))
            if not not_done_bo_moves:
                continue
            picking_sequence = ''
            if self.sale_order_id:
                picking_sequence = self.env['ir.sequence'].next_by_code('sale.workorder')

            backorder_picking = picking.copy({
                'name': picking_sequence and picking_sequence or '/',
                'move_lines': [],
                'pack_operation_ids': [],
                'backorder_id': picking.id
            })
            picking.message_post(body=_("Back order <em>%s</em> <b>created</b>.") % (backorder_picking.name))
            not_done_bo_moves.write({'picking_id': backorder_picking.id})
            if not picking.date_done:
                picking.write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            backorder_picking.action_confirm()
            backorder_picking.action_assign()
            backorders |= backorder_picking

            if self.sale_order_id:
                pack = []

                for recline in backorder_picking.move_lines:
                    recline.state = 'assigned'
                    pack.append([0, 0, {
                        'product_id': recline.product_id.id,
                        'product_uom_qty': recline.product_uom_qty,
                        'ordered_qty': recline.product_uom_qty,
                        'product_qty': recline.product_uom_qty,
                        'product_uom_id': recline.product_uom.id,
                        'name': recline.product_id.name,
                        'location_dest_id': self.partner_id.property_stock_customer.id,
                        'location_id': self.location_id.id,
                    }])
                backorder_picking.pack_operation_ids = pack
        return backorders

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for line in self:
            if sum([x.qty_done for x in line.pack_operation_ids]):
                line.sale_order_id.order_line._compute_done_wo_count()
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    sale_order_id = fields.Many2one('sale.order', related='picking_id.sale_order_id', store=True)