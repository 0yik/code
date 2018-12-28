# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.onchange('date_order')
    def onchange_date_order(self):
        if self.date_order:
            for line in self.order_line:
                line.product_uom_change()

class sale_order_line(models.Model):

    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty','order_id.date_order')
    def product_uom_change(self):
        super(sale_order_line, self).product_uom_change()
        customers = self.env['product.customerinfo'].search([
            ('name', '=', self.order_id.partner_id.id),
            ('product_template_id', '=', self.product_id.product_tmpl_id.id),
        ])
        if customers and self.product_uom_qty >= customers.min_qty :
            flag = True
            order_date = datetime.strptime(self.order_id.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
            if customers.date_start :
                date_start = datetime.strptime(customers.date_start, DEFAULT_SERVER_DATE_FORMAT)
                if date_start > order_date:
                    flag = False
            if customers.date_end:
                date_end = datetime.strptime(customers.date_end, DEFAULT_SERVER_DATE_FORMAT)
                if date_end < order_date:
                    flag = False
            if flag:
                self.price_unit = customers.price


    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            super(sale_order_line, self).product_id_change()
            customers = self.env['product.customerinfo'].search([
                ('name', '=', self.order_id.partner_id.id),
                ('product_template_id', '=', self.product_id.product_tmpl_id.id),
            ])
            if customers:
                product_name = ''
                if customers.product_code:
                    product_name += '[' + customers.product_code + '] '
                else:
                    product_name += '[' + self.product_id.default_code + '] '

                if customers.product_name:
                    product_name += customers.product_name
                else:
                    product_name += self.product_id.name
                if product_name != '':
                    self.name = product_name