# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_work_order_count(self):
        for order in self:
            orders = self.env['stock.picking'].search([('sale_order_id','=', order.id)])
            order.work_order_count = len(orders)

    work_order_count = fields.Integer('Completed Work Order ', compute='_compute_work_order_count')

    @api.multi
    def action_view_workorder(self):
        for rec in self:
            workorder = self.env['stock.picking'].search([('sale_order_id', '=', rec.id)])
            action = self.env.ref('stock.action_picking_tree_all').read()[0]
            if len(workorder) > 1:
                action['domain'] = [('id', 'in', workorder.ids)]
                action['display_name'] = "Work Order"
            elif len(workorder) == 1:
                action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
                action['res_id'] = workorder.ids[0]
                action['display_name'] = "Work Order"
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            picking_sequence = self.env['ir.sequence'].next_by_code('sale.workorder')
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
            source_location = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
            move = []
            pack = []
            for recline in rec.order_line:
                if recline.product_id.type == 'service':
                    move.append([0, 0, {
                        'product_id': recline.product_id.id,
                        'product_uom_qty': recline.product_uom_qty,
                        'product_uom': recline.product_uom.id,
                        'name': recline.product_id.name,
                        'state': 'assigned'
                    }
                                 ])
                    pack.append([0, 0, {
                        'product_id': recline.product_id.id,
                        'product_uom_qty': recline.product_uom_qty,
                        'ordered_qty': recline.product_uom_qty,
                        'product_qty': recline.product_uom_qty,
                        'product_uom_id': recline.product_uom.id,
                        'name': recline.product_id.name,
                        'location_dest_id': rec.partner_id.property_stock_customer.id,
                        'location_id': source_location.id,
                    }
                                 ])
            work_order = {
                'partner_id': rec.partner_id.id,
                'location_dest_id': rec.partner_id.property_stock_customer.id,
                'location_id': source_location.id,
                'picking_type_id': picking_type.id,
                'move_lines': move,
                'pack_operation_product_ids': pack,
                'sale_order_id': rec.id,
                'name': picking_sequence,
                'origin': rec.name,

            }
            if move:
                workorder = self.env['stock.picking'].create(work_order)
        return res



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _compute_done_wo_count(self):
        for line in self:
            qty = 0.0
            qty_done = 0.0
            picking_ids = self.env['stock.picking'].search([('sale_order_id','=', line.order_id.id)])
            packing_ids = self.env['stock.pack.operation'].search([('picking_id', 'in', ([x.id for x in picking_ids])),('product_id', '=', line.product_id.id)])
            for items in packing_ids:
                qty_done += items.qty_done
                qty += items.product_qty
            line.done_wo_count = qty_done
            line.wo_count_update = qty

    done_wo_count = fields.Float('Work Order Done', compute='_compute_done_wo_count', store=True)
    wo_count_update = fields.Float('Work Order Quantity', compute='_compute_done_wo_count', store=True)

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state', 'done_wo_count',
                 'product_id.workorder_invoice_policy')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['sale', 'done']:
                if line.product_id.type == 'service' and line.product_id.workorder_invoice_policy == 'workorder':
                    line.qty_to_invoice = line.done_wo_count - line.qty_invoiced
                elif line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.wo_count_update - line.qty_invoiced
            else:
                line.qty_to_invoice = 0