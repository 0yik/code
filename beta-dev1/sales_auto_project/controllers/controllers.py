# -*- coding: utf-8 -*-
from odoo import http

# class SalesAutoProject(http.Controller):
#     @http.route('/sales_auto_project/sales_auto_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_auto_project/sales_auto_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_auto_project.listing', {
#             'root': '/sales_auto_project/sales_auto_project',
#             'objects': http.request.env['sales_auto_project.sales_auto_project'].search([]),
#         })

#     @http.route('/sales_auto_project/sales_auto_project/objects/<model("sales_auto_project.sales_auto_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_auto_project.object', {
#             'object': obj
#         })