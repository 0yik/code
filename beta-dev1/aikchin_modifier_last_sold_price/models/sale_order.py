# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    last_sold_price = fields.Float('Last Sold Price')
    last_sold_date = fields.Date('Last Sold Date')

    # @api.onchange('product_id', 'product_uom_qty')
    # def _onchange_product_id_check_availability(self):
    #     if self.product_id and self.order_id and self.order_id.partner_id:
    #         sale_orders = self.env['sale.order'].search([('partner_id', '=', self.order_id.partner_id.id)],
    #                                                     order='create_date desc')
    #         for sale_order in sale_orders:
    #             is_find = False
    #             for order_line in sale_order.order_line:
    #                 if order_line.product_id == self.product_id:
    #                     self.last_sold_price = order_line.price_unit
    #                     self.last_sold_date = sale_order.date_order
    #                     is_find = True
    #             if is_find: break
    #         if not self.last_sold_price:
    #             self.last_sold_price = self.price_unit
    #         if not self.last_sold_date:
    #             self.last_sold_date = datetime.now()
    #     res = super(SaleOrderLine, self)._onchange_product_id_check_availability()
    #     return res

    @api.onchange('product_id')
    def _onchange_product_id_uom_check_availability(self):
        if self.product_id  and self.order_id and self.order_id.partner_id:
            sale_orders = self.env['sale.order'].search([('partner_id', '=', self.order_id.partner_id.id)], order='create_date desc')
            for sale_order in sale_orders:
                is_find = False
                for order_line in sale_order.order_line:
                    if order_line.product_id == self.product_id:
                        self.last_sold_price = order_line.price_unit
                        self.last_sold_date = sale_order.date_order
                        is_find = True
                if is_find: break
            if not self.last_sold_price:
                self.last_sold_price = self.price_unit
            if not self.last_sold_date:
                self.last_sold_date = datetime.now()
        res = super(SaleOrderLine, self)._onchange_product_id_uom_check_availability()
        return res

