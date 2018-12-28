# -*- coding: utf-8 -*-
from odoo import http

# class CustomerProfilingSales(http.Controller):
#     @http.route('/customer_profiling_sales/customer_profiling_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_profiling_sales/customer_profiling_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_profiling_sales.listing', {
#             'root': '/customer_profiling_sales/customer_profiling_sales',
#             'objects': http.request.env['customer_profiling_sales.customer_profiling_sales'].search([]),
#         })

#     @http.route('/customer_profiling_sales/customer_profiling_sales/objects/<model("customer_profiling_sales.customer_profiling_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_profiling_sales.object', {
#             'object': obj
#         })