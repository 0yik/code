# -*- coding: utf-8 -*-
from odoo import http

# class SalesCostPriceEncryption(http.Controller):
#     @http.route('/sales_cost_price_encryption/sales_cost_price_encryption/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_cost_price_encryption/sales_cost_price_encryption/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_cost_price_encryption.listing', {
#             'root': '/sales_cost_price_encryption/sales_cost_price_encryption',
#             'objects': http.request.env['sales_cost_price_encryption.sales_cost_price_encryption'].search([]),
#         })

#     @http.route('/sales_cost_price_encryption/sales_cost_price_encryption/objects/<model("sales_cost_price_encryption.sales_cost_price_encryption"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_cost_price_encryption.object', {
#             'object': obj
#         })