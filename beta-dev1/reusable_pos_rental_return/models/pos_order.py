# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.multi
    def perform_button_operation(self, operation):
        if operation == 'returned':
            StockPicking = self.env['stock.picking']
            today = fields.Date.from_string(fields.Date.today())

            for order in self.filtered(lambda o: o.collected and not o.returned):
                booking_lines = order.booking_id.booking_lines

                # early return
                movelines = StockPicking.search([('booking_order_id', '=', order.booking_id.id)]).filtered(lambda p: p.picking_type_id.code == 'incoming').move_lines
                for line in booking_lines:
                    if fields.Date.from_string(line.end_date) > today:
                        laundry_days = (fields.Date.from_string(line.actual_end_date) - fields.Date.from_string(line.end_date)).days
                        move = movelines.filtered(lambda m: m.product_id == line.product_id)
                        move.date_expected = today
                        line.end_date = today
                        if laundry_days != 0:
                            line.actual_end_date = today + timedelta(days=laundry_days)
                        else:
                            line.actual_end_date = today

        return super(PosOrder, self).perform_button_operation(operation)
