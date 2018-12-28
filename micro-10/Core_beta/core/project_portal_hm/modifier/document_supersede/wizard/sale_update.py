# -*- coding: utf-8 -*-
import time
from odoo import models, api, _, fields

class sale_update(models.TransientModel):
    _name = 'sale.update'
    _description = 'Sale Update'
    
    def _get_order(self):
        return self._context['active_id']
    
    def _get_order_lines(self):
        order_lines = []
        order = self.env['sale.order'].browse(self._context['active_id'])
        for line in order.order_line:
            order_lines.append({
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'sub_total': line.product_uom_qty * line.price_unit,
                'order_line_id': line.id
            })
        return order_lines
    
    @api.one
    @api.depends('order_lines', 'order_lines.quantity', 'order_lines.price_unit')
    def _total(self):
        total = 0
        for line in self.order_lines:
            total += line.quantity * line.price_unit
        self.amount_total = total


    sale_id      = fields.Many2one('sale.order', 'Sale Order', default=_get_order)
    order_lines  = fields.One2many('sale.update.line', 'sale_id', 'Lines', default=_get_order_lines)
    amount_total = fields.Float('Total Amount', compute=_total)
    
    @api.one
    def action_update(self):
        order = self.sale_id
        version = self.env['sale.version'].create({
            'name': order.name,
            'update_user_id': self.env.user.id,
            'update_date': time.strftime('%Y-%m-%d'),
            'sale_id': order.id
        })
        for line in order.order_line:
            self.env['sale.version.line'].create({
                'version_id': version.id,
                'product_id': line.product_id and line.product_id.id or False ,
                'name': line.name,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit
            })
        for line in self.order_lines:
            if line.order_line_id:
                line.order_line_id.write({
                    'product_id': line.product_id and line.product_id.id or False ,
                    'name': line.name,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.price_unit
                })
            else:
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': line.product_id and line.product_id.id or False ,
                    'name': line.name,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.price_unit
                })
        new_version = order.version_no + 1
        order.version_no = new_version
        order.name = order.name.split('(')[0] + '(' + str(new_version) + ')' 
        return {'type': 'ir.actions.act_window_close'}

class sale_update_line(models.TransientModel):
    _name = 'sale.update.line'
    _description = 'Sale Update Lines'
    
    @api.one
    @api.depends('price_unit', 'quantity')
    def _subtotal(self):
        self.sub_total = self.quantity * self.price_unit

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.name = self.product_id.name
        
    sale_id       = fields.Many2one('sale.update', 'Invoice')
    order_line_id = fields.Many2one('sale.order.line', 'Order Line')
    product_id    = fields.Many2one('product.product', 'Product')
    name          = fields.Char('Description')
    quantity      = fields.Float('Quantity')
    price_unit    = fields.Float('Unit Price')
    sub_total     = fields.Float('Amount', compute=_subtotal)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: