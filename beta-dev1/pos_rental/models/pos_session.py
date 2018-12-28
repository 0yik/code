# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _total_booking_deposit(self):
        for obj in self:
            order_ids = self.env['pos.order'].search([('session_id','=',obj.id),('booking_id','!=',False)])
            invoice_ids = [o.invoice_id.id for o in order_ids ]
            obj.total_refundable =  sum(self.env['account.invoice.line'].search([('invoice_id','in',invoice_ids),('product_id.type','=','service')]).mapped('price_subtotal'))
            
    def _total_refundable_deposit(self):
        for obj in self:
            order_ids = self.env['pos.order'].search([('session_id','=',obj.id),('booking_id','!=',False)])
            if any(order_ids):
                rental_product = self.env.ref('pos_rental.product_product_advance_payment').id
                self.env.cr.execute('select sum(qty*price_unit) from pos_order_line where product_id=%s and order_id IN %s',(rental_product,tuple(order_ids.ids)))
                total_refund = self.env.cr.fetchall()[0][0]
                if total_refund:
                    obj.refunded_deposit = total_refund
                    
    total_refundable = fields.Float(compute='_total_booking_deposit',string="Booking Deposit")
    refunded_deposit = fields.Float(compute='_total_refundable_deposit',string="Refundable Deposit")
    
