# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime,time
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning, ValidationError

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'
    

    booking_order_line_ids = fields.Many2many('booking.order.line',string='Booking Order Line', domain="[('state','=','draft'),('order_id','!=',False)]")

    @api.multi
    def validate_booking_order_line(self):
        repeat_list = []
        picking_obj = self.env['stock.picking']
        user_obj = self.env['res.users'].browse(self._uid)
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', user_obj.company_id.id)],
                                                                  limit=1)
        type_id = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_id[0].id), ('code', '=', 'outgoing')], limit=1)
        location_id = self.env['stock.location'].search(
                        [('company_id', '=', user_obj.company_id.id), ('usage', '=', 'internal')], limit=1)
        location_dest_id = self.env['stock.location'].search(
                        [('usage', '=', 'customer')], limit=1)
        for line_id in self.booking_order_line_ids:
            already_booked_product = line_id.search([
                ('product_id','=',line_id.product_id.id),
                ('order_id','!=',line_id.order_id.id),
                ('state','in',['pending','out']),
                ])
            for exist_line_id in already_booked_product:
                if line_id.start_date >= exist_line_id.actual_start_date and line_id.start_date <= exist_line_id.actual_end_date:
                    raise Warning(_('Product Already booked in order %s') % exist_line_id.order_id.name)
                if line_id.end_date >= exist_line_id.actual_start_date and line_id.start_date <= exist_line_id.actual_end_date:
                    raise Warning(_('Product Already booked in order %s') % exist_line_id.order_id.name)
            for main in self.booking_order_line_ids:
                if main.id != line_id.id and main.id not in repeat_list:
                    if main.product_id == line_id.product_id:
                        repeat_list.append(main.id)
                        if line_id.start_date >= main.actual_start_date and line_id.start_date <= main.actual_end_date:
                            raise Warning(_('You can not select same product for booked in same datetime'))
                        if line_id.end_date >= main.actual_start_date and line_id.start_date <= main.actual_end_date:
                            raise Warning(_('You can not select same product for booked in same datetime'))
            # already_stock_picking_id = self.env['stock.picking'].search([('booking_order_id','=',line_id.order_id.id)])
            # stock_picking_id = False
            # if not already_stock_picking_id:
            #     stock_picking_id = self.env['stock.picking'].create({
            #         'partner_id':self.partner_id and self.partner_id.id or False,
            #         'picking_type_id': type_id.id or False,
            #         'location_id': location_id and location_id.id or False,
            #         'location_dest_id': location_dest_id and location_dest_id.id or False,
            #         'booking_order_id':line_id.order_id.id,
            #     })
            # self.env['stock.move'].create({
            #         'name': line_id.product_id.name,
            #         'product_id':line_id.product_id and line_id.product_id.id or False,
            #         'product_uom_qty':1,
            #         'product_uom': line_id.product_id and line_id.product_id.uom_id and line_id.product_id.uom_id.id or False,
            #         'location_id': location_id and location_id.id or False,
            #         'location_dest_id': location_dest_id and location_dest_id.id or False,
            #         'picking_id':stock_picking_id and stock_picking_id.id or already_stock_picking_id and already_stock_picking_id.id or False,
            #         })
            if line_id.order_id:
                line_id.state = 'pending'
                out_stock_picking_id = picking_obj.search([('min_date','=',line_id.start_date),('state','=','draft')])
                if not out_stock_picking_id:
                        out_stock_picking_id = line_id.order_id.create_stock_picking('do_out')
                in_stock_picking_id = picking_obj.search([('min_date','=',line_id.end_date),('state','=','draft')])
                if not in_stock_picking_id:
                        in_stock_picking_id = line_id.order_id.create_stock_picking('do_in')
                line_id.order_id.create_move_for_picking(line_id, out_stock_picking_id, 'do_out')
                line_id.order_id.create_move_for_picking(line_id, in_stock_picking_id, 'do_in')
            self.env['product.serial.number'].create({
                'product_id':line_id.product_id.id,
                'serial_no': line_id.product_id.serial_no,
                'booking_line_id': line_id.id,
                'booking_order_id':line_id.order_id.id,
                'actual_start_date': line_id.actual_start_date,
                'actual_end_date': line_id.actual_end_date,
                })
            line_id.state = 'pending'
            line_id.order_id.state = 'pending'
