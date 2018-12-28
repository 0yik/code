# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime,timedelta
from odoo.tools import email_re, float_is_zero
from odoo.exceptions import UserError, ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.multi
    def action_pos_order_invoice(self):
        result = super(PosOrder, self).action_pos_order_invoice()
        if result.get('res_id') and self.online_order:
            reg_payment_env = self.env['account.payment']
            invoice_id = result.get('res_id')
            self.env['account.invoice'].browse(result.get('res_id')).action_invoice_open()#validate the created invoice
            reg_payment_data = reg_payment_env.with_context(default_invoice_ids=[(4, invoice_id, None)]).default_get(['communication', 'currency_id', 'invoice_ids', 'payment_difference', 'partner_id', 'payment_method_id', 'payment_difference_handling', 'journal_id', 'state', 'writeoff_account_id', 'payment_date', 'partner_type', 'payment_token_id', 'hide_payment_method', 'payment_method_code', 'amount', 'payment_type'])
            journal_id = self.statement_ids[0].statement_id.journal_id.id
            reg_payment_data.update({'journal_id': journal_id,
                    'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,})
            reg_payment_id = reg_payment_env.sudo().with_context(active_model='account.invoice',active_ids=invoice_id).create(reg_payment_data)
            payment_data = reg_payment_id.post()

        return result
        
    #This method is used to pass the invoice type i.e rental or sale
    def _prepare_invoice(self):
        res = super(PosOrder,self)._prepare_invoice()
        if self.booking_id:
            end_date = self.booking_id.booking_lines.mapped('end_date')[0]
            res.update({'inv_for':'rental','booking_end_date':end_date})
        else:
            res.update({'inv_for':'sale'})
        return res

    # make outgoing picking per order for customer collection
    def create_collect_picking(self):
        picking_id = False
        StockPicking = self.env['stock.picking']
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        outgoing_type = self.env['stock.picking.type'].search([('warehouse_id', '=', warehouse.id), ('code', '=', 'outgoing')], limit=1)
        src_location_id = outgoing_type.default_location_src_id.id
        dest_location_id = self.env.ref('modifier_ccm_pos_rental.ccm_stock_location_rented_out').id
        vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': outgoing_type.id,
            'location_id': src_location_id,
            'location_dest_id': dest_location_id,
            'booking_order_id': self.booking_id.id,
            'pos_order_id': self.id,
        }
        picking = self.env['stock.picking'].create(vals)
        for line in self.booking_id.booking_lines:
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom': line.product_id and line.product_id.uom_id.id or False,
                'product_uom_qty': 1,
                'picking_id': picking.id,
                'booking_order_line_id': line.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'date_expected': line.start_date,
            }
            self.env['stock.move'].create(move_vals)
        picking.action_confirm()
        picking.force_assign()
        for operation in picking.pack_operation_product_ids:
            operation.qty_done = operation.product_qty
        picking.do_new_transfer()
        return True

    # make incoming picking per order for customer return
    def create_return_picking(self):
        picking_id = False
        StockPicking = self.env['stock.picking']
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        incoming_type = self.env['stock.picking.type'].search([('warehouse_id', '=', warehouse.id), ('code', '=', 'incoming')], limit=1)
        dest_location_id = incoming_type.default_location_dest_id.id
        src_location_id = self.env.ref('modifier_ccm_pos_rental.ccm_stock_location_rented_out').id
        vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': incoming_type.id,
            'location_id': src_location_id,
            'location_dest_id': dest_location_id,
            'booking_order_id': self.booking_id.id,
            'pos_order_id': self.id,
        }
        picking = self.env['stock.picking'].create(vals)
        for line in self.booking_id.booking_lines:
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom': line.product_id and line.product_id.uom_id.id or False,
                'product_uom_qty': 1,
                'picking_id': picking.id,
                'booking_order_line_id': line.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'date_expected': line.end_date,
            }
            self.env['stock.move'].create(move_vals)
        picking.action_confirm()
        picking.force_assign()
        for operation in picking.pack_operation_product_ids:
            operation.qty_done = operation.product_qty
        picking.do_new_transfer()
        return True

    # set destination location to laundry using Laundry order picking type
    @api.multi
    def create_laundry_picking(self):
        picking_type_id = self.env['stock.picking.type'].search([('name', '=', 'Laundry Orders')], limit=1)
        pick_vals = {
            'partner_id': self.partner_id.id,
            'move_type': 'direct',
            'picking_type_id': picking_type_id.id,
            'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'booking_order_id': self.booking_id.id,
            'pos_order_id': self.id,
        }
        picking = self.env['stock.picking'].create(pick_vals)
        for line in self.lines.filtered(lambda line:line.product_id.type != 'service'):
            move_vals = {
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uom_qty': line.qty,
                'name': line.product_id.name,
                'date_expected': datetime.now(),
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            }
            move_id = self.env['stock.move'].create(move_vals)
        picking.action_confirm()
        picking.force_assign()
        for operation in picking.pack_operation_product_ids:
            operation.qty_done = operation.product_qty
        picking.do_new_transfer()
        return True

    # set source location to laundry for available operation
    @api.multi
    def create_laundry_return_picking(self):
        laundry_location = self.env.ref('modifier_ccm_pos_rental.stock_location_laundry')
        picking_type_id = self.env['stock.picking.type'].search([('name', '=', 'Receipts')], limit=1)
        pick_vals = {
            'partner_id': self.partner_id.id,
            'move_type': 'direct',
            'picking_type_id': picking_type_id.id,
            'location_id': laundry_location.id,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'booking_order_id': self.booking_id.id,
            'pos_order_id': self.id,
        }
        picking = self.env['stock.picking'].create(pick_vals)
        for line in self.lines.filtered(lambda line:line.product_id.type != 'service'):
            move_vals = {
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uom_qty': line.qty,
                'name': line.product_id.name,
                'date_expected': datetime.now(),
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            }
            move_id = self.env['stock.move'].create(move_vals)
        picking.action_confirm()
        picking.force_assign()
        for operation in picking.pack_operation_product_ids:
            operation.qty_done = operation.product_qty
        picking.do_new_transfer()
        return True

    @api.multi
    def perform_button_operation(self, operation):
        if operation in ('laundry', 'available'):
            return super(PosOrder, self).perform_button_operation(operation)
        else:
            error = False
            message = ""
            StockPicking = self.env['stock.picking']

            for order in self:
                if operation == "collected":
                    if order.collected:
                        error = True
                        message = "Order already collected."
                    elif order.returned:
                        error = True
                        message = "Order is already returned by the Customer. Order cannot be collected."
                    elif order.laundry:
                        error = True
                        message = "Order is with vendor for laundry. Order cannot be collected."
                    elif order.all_done:
                        error = True
                        message = "All processes associated with this order are complete. Order cannot be collected."
                    else:
                        order.create_collect_picking()
                        order.write({'collected': True, 'order_status': 'Order-Collected'})
                elif operation == "returned":
                    if not order.collected:
                        error = True
                        message = "Order is not collected by customer. Order cannot be returned"
                    elif order.returned:
                        error = True
                        message = "Order is already returned by the Customer. Order cannot be returned."
                    elif order.laundry:
                        error = True
                        message = "Order is with vendor for laundry. Order cannot be returned."
                    elif order.all_done:
                        error = True
                        message = "All processes associated with this order are complete. Order cannot be returned."
                    else:
                        order.create_return_picking()
                        order.write({'returned': True, 'order_status': 'Order-Returned'})
            return {
                'error': error,
                'message': message
            }


class Modifier_BookingOrder(models.Model):
    _inherit = 'booking.order'

    @api.model
    def create_from_pos_ui(self, order):
        vals = {}
        dates = []
        product = self.env['product.product'].browse(order.get('product_id'))
        for date in order['dates']:
            dates.append(datetime.strptime(date[:19], "%Y-%m-%d %H:%M:%S").date())
        start_date = min(dates)
        end_date = max(dates)
        actual_start_date = start_date - timedelta(days=product.default_preparation_days)
        actual_end_date = end_date + timedelta(days=int(order.get('buffer_days', 0)))
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        # check product is already booked for ordered product
        lines = self.env['booking.order.line'].search([('product_id', '=', product.id), ('state', '!=', 'returned')])
        for line in lines:
            start_dt, end_dt = fields.Date.from_string(line.actual_start_date), fields.Date.from_string(line.actual_end_date)
            if start_dt <= actual_start_date <= end_dt:
                return
            if start_dt <= actual_end_date <= end_dt:
                return
            if start_dt > actual_start_date and end_dt > actual_start_date and end_dt < actual_end_date:
                return

        vals['booking_lines'] = [(0, 0, {
                    'product_id': product.id,
                    'product_qty': 1,
                    'start_date': start_date,
                    'end_date': end_date,
                    'actual_start_date': actual_start_date.strftime("%Y-%m-%d"),
                    'actual_end_date': actual_end_date.strftime("%Y-%m-%d"),
                })]

        if order.get('booking_id'):
            booking = self.browse(order['booking_id'][0])
            booking.write(vals)
        else:
            vals.update({
                'def_start_date': actual_start_date,
                'def_end_date': actual_end_date,
                'partner_id': order['partner_id'],
            })
            booking = self.create(vals)
        return [booking.id, booking.name, booking.def_start_date, booking.def_end_date]
