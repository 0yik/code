# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime,time
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning, ValidationError

class BookingOrder(models.Model):
    _name = 'booking.order'
    _description = 'Booking Orders'
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('booking.order') or 'New'
        result = super(BookingOrder, self).create(vals)
        return result

    name = fields.Char(string="Name", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner',string="Customer")
    def_start_date = fields.Date(string='Default Start Date', required=True)
    def_end_date = fields.Date(string='Default End Date', required=True)
    customer_remarks = fields.Text(string="Customer's Remarks")
    location = fields.Char(string='Location')
    user_id = fields.Many2one('res.users',string="Salesperson")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('out', 'Out'),
        ('returned', 'Returned'),
        ('sold', 'Sold'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')
    booking_lines = fields.One2many('booking.order.line','order_id',string="Booking Lines")
    
    @api.multi
    def _count_bookings(self):
        self.count_bookings = self.env['product.serial.number'].search_count([('booking_order_id','=', self.id)])
    
    @api.multi
    def _count_delivery(self):
        self.count_delivery = self.env['stock.picking'].search_count([('booking_order_id','=', self.id)])

    @api.multi
    def _count_invoices(self):
        self.count_invoices = self.env['account.invoice'].search_count([('booking_order_id','=', self.id)])

    count_bookings = fields.Integer(compute=_count_bookings)
    count_delivery = fields.Integer(compute=_count_delivery)
    count_invoices = fields.Integer(compute=_count_invoices)

    @api.multi
    def unlink(self):
        for booking_order_id in self:
            if booking_order_id.state != 'draft':
                raise Warning(_('You can delete only draft booking order'))
        return super(BookingOrder, self).unlink()
    
    @api.multi
    def sell_product(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            sell_product_form_id = ir_model_data.get_object_reference('product_booking', 'view_sell_product_wizard')[1]
        except ValueError:
            sell_product_form_id = False

        for line in self.booking_lines:
            line.product_id.booking_order_line_id = line.id

        booking_products = [line.product_id.id for line in self.booking_lines]
        sell_pro_id = self.env['sell.product'].create({'product_ids':[(6, 0, booking_products)]})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sell.product',
            'res_id':sell_pro_id.id,
            'views': [(sell_product_form_id, 'form')],
            'view_id': sell_product_form_id,
            'target': 'new',
        }

    @api.multi
    def create_stock_picking(self, do_type):
        picking_id = False
        picking_obj = self.env['stock.picking']
        user_obj = self.env['res.users'].browse(self._uid)
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', user_obj.company_id.id)],
                                                                  limit=1)
        outgoing_type_id = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_id[0].id), ('code', '=', 'outgoing')], limit=1)
        incoming_type_id = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_id[0].id), ('code', '=', 'incoming')], limit=1)
        out_location_dest_id = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1)
        in_location_id = self.env['stock.location'].search(
                        [('usage', '=', 'supplier')], limit=1)
        physical_location_id = self.env['ir.model.data'].get_object_reference('stock','stock_location_locations')
        wh_location_id = self.env['stock.location'].search(
                        [('company_id', '=', user_obj.company_id.id),
                        ('location_id', '=', physical_location_id and physical_location_id[1]),
                        ('usage', '=', 'view')], limit=1)
        stock_location_id = self.env['stock.location'].search(
                        [('company_id', '=', user_obj.company_id.id),
                        ('location_id', '=', wh_location_id and wh_location_id.id),
                        ('usage', '=', 'internal')], limit=1)
        if do_type == 'do_out':        
            vals = {
                'partner_id':self.partner_id and self.partner_id.id or False,
                'picking_type_id': outgoing_type_id.id or False,
                'location_id': stock_location_id and stock_location_id.id or False,
                'location_dest_id': out_location_dest_id and out_location_dest_id.id or False,
                'booking_order_id':self.id or False,
                }
            picking_id = self.env['stock.picking'].create(vals)
        if do_type == 'do_in':
            vals = {
                'partner_id':self.partner_id and self.partner_id.id or False,
                'picking_type_id': incoming_type_id.id or False,
                'location_id': in_location_id and in_location_id.id or False,
                'location_dest_id': stock_location_id and stock_location_id.id or False,
                'booking_order_id':self.id or False,
                }
            picking_id = self.env['stock.picking'].create(vals)
        return picking_id

    @api.multi
    def create_move_for_picking(self, line_id, in_out_picking_id, do_type):
        vals = {}
        move_obj = self.env['stock.move']
        user_obj = self.env['res.users'].browse(self._uid)
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', user_obj.company_id.id)],
                                                                  limit=1)
        outgoing_type_id = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_id[0].id), ('code', '=', 'outgoing')], limit=1)
        incoming_type_id = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_id[0].id), ('code', '=', 'incoming')], limit=1)
        out_location_dest_id = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1)
        in_location_id = self.env['stock.location'].search(
                        [('usage', '=', 'supplier')], limit=1)
        physical_location_id = self.env['ir.model.data'].get_object_reference('stock','stock_location_locations')
        wh_location_id = self.env['stock.location'].search(
                        [('company_id', '=', user_obj.company_id.id),
                        ('location_id', '=', physical_location_id and physical_location_id[1]),
                        ('usage', '=', 'view')], limit=1)
        stock_location_id = self.env['stock.location'].search(
                        [('company_id', '=', user_obj.company_id.id),
                        ('location_id', '=', wh_location_id and wh_location_id.id),
                        ('usage', '=', 'internal')], limit=1)
        vals = {
                'name': line_id.product_id.name,
                'product_id':line_id.product_id and line_id.product_id.id or False,
                'product_uom_qty':1,
                'product_uom': line_id.product_id and line_id.product_id.uom_id and line_id.product_id.uom_id.id or False,
                'picking_id':in_out_picking_id and in_out_picking_id.id or False,
                'booking_order_line_id':line_id.id,
            }

        if in_out_picking_id and do_type == 'do_out':
           vals.update({
                'location_id': stock_location_id and stock_location_id.id or False,
                'location_dest_id': out_location_dest_id and out_location_dest_id.id or False,
                'date_expected':line_id.start_date,
                'picking_type_id':outgoing_type_id and outgoing_type_id.id or False,
            })
        if in_out_picking_id and do_type == 'do_in':
            vals.update({
                'location_id': in_location_id and in_location_id.id or False,
                'location_dest_id': stock_location_id and stock_location_id.id or False,
                'date_expected':line_id.end_date,
                'picking_type_id':incoming_type_id and incoming_type_id.id or False,
                })
        return move_obj.create(vals)


    @api.multi
    def validate_booking(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        for line in self.booking_lines:
            already_booked_product = line.search([
                ('product_id','=',line.product_id.id),
                ('order_id','!=',self.id),
                ('state','in',['pending','out']),
                ])
            for exist_line_id in already_booked_product:
                if line.start_date >= exist_line_id.actual_start_date and line.start_date <= exist_line_id.actual_end_date:
                    raise Warning(_('Product Already booked in order %s') % exist_line_id.order_id.name)
                if line.end_date >= exist_line_id.actual_start_date and line.start_date <= exist_line_id.actual_end_date:
                    raise Warning(_('Product Already booked in order %s') % exist_line_id.order_id.name)
        out_stock_picking_id = False
        in_stock_picking_id = False
        self.state = 'pending'
        for line_id in  self.booking_lines:
            line_id.state = 'pending'
            out_stock_picking_id = picking_obj.search([('min_date','=',line_id.start_date),('state','=','draft')])
            if not out_stock_picking_id:
                out_stock_picking_id = self.create_stock_picking('do_out')
            in_stock_picking_id = picking_obj.search([('min_date','=',line_id.end_date),('state','=','draft')])
            if not in_stock_picking_id:
                in_stock_picking_id = self.create_stock_picking('do_in')
            self.create_move_for_picking(line_id, out_stock_picking_id, 'do_out')
            self.create_move_for_picking(line_id, in_stock_picking_id, 'do_in')
            self.env['product.serial.number'].create({
                'product_id':line_id.product_id.id,
                'serial_no': line_id.product_id.serial_no,
                'booking_line_id': line_id.id,
                'booking_order_id':self.id,
                'actual_start_date': line_id.actual_start_date,
                'actual_end_date': line_id.actual_end_date,
                })


class BookingOrderLine(models.Model):
    _name = 'booking.order.line'
    _description = 'Booking Order Lines'
    
    product_id = fields.Many2one('product.product', string='Product', required=True)
    serial_no = fields.Char(string='Product’s Serial No.', related='product_id.serial_no' , required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    actual_start_date = fields.Date(string='Actual Start Date', required=True)
    actual_end_date = fields.Date(string='Actual End Date', required=True)
    order_id = fields.Many2one('booking.order')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('out', 'Out'),
        ('returned', 'Returned'),
        ('sold', 'Sold'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')

    
    @api.onchange('start_date','product_id')
    @api.multi
    def OnChnageStartDate(self):
        if self.product_id and self.start_date:
            days = int(self.product_id.default_preparation_days)
            start_date = datetime.strptime(self.start_date,"%Y-%m-%d")
            self.actual_start_date = (start_date - relativedelta(days=days)).strftime("%Y-%m-%d")
        
    @api.onchange('end_date','product_id')
    @api.multi
    def OnChnageEndDate(self):
        if self.product_id and self.end_date:
            days = int(self.product_id.default_buffer_days)
            end_date = datetime.strptime(self.end_date,"%Y-%m-%d")
            self.actual_end_date = (end_date + relativedelta(days=days)).strftime("%Y-%m-%d")
    



