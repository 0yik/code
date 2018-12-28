# -*- coding: utf-8 -*-
from odoo import http

# class SalesRowPerView(http.Controller):
#     @http.route('/sales_row_per_view/sales_row_per_view/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_row_per_view/sales_row_per_view/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_row_per_view.listing', {
#             'root': '/sales_row_per_view/sales_row_per_view',
#             'objects': http.request.env['sales_row_per_view.sales_row_per_view'].search([]),
#         })

#     @http.route('/sales_row_per_view/sales_row_per_view/objects/<model("sales_row_per_view.sales_row_per_view"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_row_per_view.object', {
#             'object': obj
#         })