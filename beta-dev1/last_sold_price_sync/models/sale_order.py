# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import models, api


class sale_saleorder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_last_sold_price(self, product_id, client_id):
        last_price = last_date = sale_order_line_cmp = pos_order_line_cmp = order = None
        if product_id and client_id:
            sale_orders = self.env['sale.order'].search([('partner_id', '=', client_id)], order='create_date desc')
            pos_orders = self.env['pos.order'].search([('partner_id', '=', client_id)], order='create_date desc')
            for sale_order in sale_orders:
                for order_line in sale_order.order_line:
                    if order_line.product_id.id == product_id:
                        sale_order_line_cmp = order_line
                break
            for pos_order in pos_orders:
                for order_line in pos_order.lines:
                    if order_line.product_id.id == product_id:
                        pos_order_line_cmp = order_line
                break
            if pos_order_line_cmp and not sale_order_line_cmp:
                order = pos_order_line_cmp
            elif not pos_order_line_cmp and sale_order_line_cmp:
                order = sale_order_line_cmp
            elif pos_order_line_cmp and sale_order_line_cmp:
                date_sale = datetime.strptime(sale_order_line_cmp.create_date, "%Y-%m-%d %H:%M:%S")
                date_pos = datetime.strptime(pos_order_line_cmp.create_date, "%Y-%m-%d %H:%M:%S")
                order = date_sale > date_pos and sale_order_line_cmp or pos_order_line_cmp
            if order:
                if order.last_sold_price:
                    last_price = order.last_sold_price
                    if order.last_sold_date:
                        last_date = order.last_sold_date
        if not last_price or last_price == 0.0:
            last_price = ""
        if not last_date:
            last_date = ""

        return last_date, last_price
