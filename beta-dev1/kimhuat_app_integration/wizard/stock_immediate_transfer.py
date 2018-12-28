# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    pick_id = fields.Many2one('stock.picking')

    @api.multi
    def process(self):
        self.ensure_one()
        # If still in draft => confirm and assign
        if self.pick_id.state == 'draft':
            self.pick_id.action_confirm()
            if self.pick_id.state != 'assigned':
                self.pick_id.action_assign()
                if self.pick_id.state != 'assigned':
                    raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
        for pack in self.pick_id.pack_operation_ids:
            if pack.product_qty > 0:
                pack.write({'qty_done': pack.product_qty})
            else:
                pack.unlink()
        self.pick_id.do_transfer()

        # function for app
        stock_obj = self.env['stock.picking'].browse(self._context.get('active_ids'))
        for wo_obj in stock_obj:
            partners = stock_obj.get_partners(wo_obj)
            vals = {}
            address = wo_obj.get_work_order_address(wo_obj)
            if address:
                subject = 'Your work order(' + str(wo_obj.name) + ') with (' + str(
                    wo_obj.partner_id.name.encode('utf-8') or '') + '), (' + str(address.encode('utf-8')) + ') is on (' + str(
                    wo_obj.scheduled_start) + ') at (' + str(wo_obj.scheduled_end) + '). Thank You.'
            else:
                subject = 'Your work order(' + str(wo_obj.name) + ') with (' + str(
                    wo_obj.partner_id.name.encode('utf-8') or '') + '), is on (' + str(
                    wo_obj.scheduled_start) + ') at (' + str(wo_obj.scheduled_end) + '). Thank You.'
            vals['work_order_id'] = wo_obj.id
            vals['customer_id'] = wo_obj.partner_id.id if wo_obj.partner_id else False
            vals['booking_name'] = wo_obj.origin if wo_obj.origin else ''
            vals['work_location'] = address if address else ''
            vals['team_id'] = wo_obj.team.id if wo_obj.team else False
            vals['team_leader_id'] = wo_obj.team_leader.id if wo_obj.team_leader else False
            vals['team_employees_ids'] = [(6, 0, partners.ids)]
            vals['subject'] = subject
            vals['state'] = 'Pending'
            vals['remarks'] = wo_obj.remarks if wo_obj.remarks else ''
            vals['created_date'] = fields.Datetime.now()
            self.env['work.order.notification'].create(vals)

StockImmediateTransfer()