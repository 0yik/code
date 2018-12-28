# -*- coding: utf-8 -*-
from odoo import http

# class SalesInventorySummary(http.Controller):
#     @http.route('/sales_inventory_summary/sales_inventory_summary/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_inventory_summary/sales_inventory_summary/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_inventory_summary.listing', {
#             'root': '/sales_inventory_summary/sales_inventory_summary',
#             'objects': http.request.env['sales_inventory_summary.sales_inventory_summary'].search([]),
#         })

#     @http.route('/sales_inventory_summary/sales_inventory_summary/objects/<model("sales_inventory_summary.sales_inventory_summary"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_inventory_summary.object', {
#             'object': obj
#         })