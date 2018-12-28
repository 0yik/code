# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    last_sold_price = fields.Float('Last Sold Price')
    last_sold_date = fields.Date('Last Sold Date')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id  and self.order_id and self.order_id.partner_id:
            pos_orders = self.env['pos.order'].search([('partner_id', '=', self.order_id.partner_id.id)], order='create_date desc')
            for pos_order in pos_orders:
                is_find = False
                for order_line in pos_order.lines:
                    if order_line.product_id == self.product_id:
                        self.last_sold_price = order_line.price_unit
                        self.last_sold_date = pos_order.date_order
                        is_find = True
                if is_find: break
            if not self.last_sold_price:
                self.last_sold_price = self.price_unit
            if not self.last_sold_date:
                self.last_sold_date = datetime.now()

    @api.model
    def create(self, vals):
        order = self.env['pos.order'].search([('id', '=', vals['order_id'])], limit=1)
        last_sold_price, last_sold_date = False, False
        if order.partner_id:
            orders = self.env['pos.order'].search(['&', ('partner_id', '=', order.partner_id.id), ('id', '!=', vals['order_id'])], order='create_date desc' )
            for pos_order in orders:
                is_find = False
                for order_line in pos_order.lines:
                    if order_line.product_id == self.product_id:
                        last_sold_price = order_line.price_unit
                        last_sold_date = pos_order.date_order
                        is_find = True
                if is_find: break
        if not last_sold_price:
            last_sold_price = vals['price_unit']
        if not last_sold_date:
            last_sold_date = datetime.now()
        vals.update({
            'last_sold_price': last_sold_price,
            'last_sold_date':last_sold_date,
        })
        res = super(pos_order_line, self).create(vals)
        return res


