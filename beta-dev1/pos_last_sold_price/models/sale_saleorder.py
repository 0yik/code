# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import models, api


class sale_saleorder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_last_sold_price(self, product_id, client_id):
        last_price = last_date = sale_order_line_cmp = pos_order_line_cmp = order = None
        if product_id and client_id:
            pos_orders = self.env['pos.order'].search([('partner_id', '=', client_id)], order='create_date desc')
            for pos_order in pos_orders:
                for order_line in pos_order.lines:
                    if order_line.product_id.id == product_id:
                        if order_line.last_sold_price:
                            last_price = order_line.last_sold_price
                            if order_line.last_sold_date:
                                last_date = order_line.last_sold_date
                break

        if not last_price or last_price == 0.0:
            last_price = ""
        if not last_date:
            last_date = ""

        return last_date, last_price
