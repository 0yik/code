# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from openerp.exceptions import Warning, ValidationError


class SellProduct(models.TransientModel):
    _name = 'sell.product'
    
    product_ids = fields.Many2many('product.product','prodoct_sell_rel','product_id','sell_id',string='Products')
    
    @api.multi
    def create_invoice(self):
        booking_order_line_list = []
        invoice_booking_order_line_list = []
        delivery_order_line_list = []
        user_obj = self.env['res.users'].browse(self._uid)
        warehouse_id = self.env['stock.warehouse'].search([
                    ('company_id', '=', user_obj.company_id.id)], limit=1)
        outgoing_type_id = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_id[0].id),
                        ('code', '=', 'outgoing')], limit=1)
        incoming_type_id = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_id[0].id),
                        ('code', '=', 'incoming')], limit=1)
        booking_order_ids = self.env['booking.order'].browse(self._context.get('active_id'))
        if not self.product_ids:
            raise (_('Please select atleast one records.'))
        invoice_id = self.env['account.invoice'].create({
            'partner_id': booking_order_ids.partner_id and booking_order_ids.partner_id.id,
            'account_id': booking_order_ids.partner_id.property_account_receivable_id.id,
            'booking_order_id': booking_order_ids.id
            })
        for line_id in self.product_ids:
            self.env['account.invoice.line'].create({
                'name': line_id.name,
                'product_id': line_id.id or False,
                'quantity':1,
                'uom_id': line_id.uom_id and line_id.uom_id.id or False,
                'price_unit': line_id.lst_price or 0.0,
                'account_id': line_id.categ_id and line_id.categ_id.property_account_income_categ_id and line_id.categ_id.property_account_income_categ_id.id,
                'invoice_id':invoice_id and invoice_id.id or False,
                })
            if line_id and line_id.booking_order_line_id:
                invoice_booking_order_line_list.append(line_id.booking_order_line_id.id)
        booking_order_line_ids = [line for line in booking_order_ids.booking_lines if line.id in invoice_booking_order_line_list]
        for line in booking_order_line_ids:
            move_ids = self.env['stock.move'].search([('product_id','=',line.product_id.id),('booking_order_line_id','in',invoice_booking_order_line_list),('picking_type_id','=',incoming_type_id.id)])
        for move in move_ids:
            move.unlink()
        if invoice_id:
            booking_order_ids.state = 'sold'
            for line in self.env['booking.order.line'].browse(invoice_booking_order_line_list):
                line.state = 'sold'
