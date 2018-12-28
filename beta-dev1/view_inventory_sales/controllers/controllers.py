# -*- coding: utf-8 -*-
from odoo import http

# class ViewInventorySales(http.Controller):
#     @http.route('/view_inventory_sales/view_inventory_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/view_inventory_sales/view_inventory_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('view_inventory_sales.listing', {
#             'root': '/view_inventory_sales/view_inventory_sales',
#             'objects': http.request.env['view_inventory_sales.view_inventory_sales'].search([]),
#         })

#     @http.route('/view_inventory_sales/view_inventory_sales/objects/<model("view_inventory_sales.view_inventory_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('view_inventory_sales.object', {
#             'object': obj
#         })