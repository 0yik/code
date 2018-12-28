# -*- coding: utf-8 -*-
from odoo import http

# class MgmSalesDashboard(http.Controller):
#     @http.route('/mgm_sales_dashboard/mgm_sales_dashboard/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgm_sales_dashboard/mgm_sales_dashboard/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgm_sales_dashboard.listing', {
#             'root': '/mgm_sales_dashboard/mgm_sales_dashboard',
#             'objects': http.request.env['mgm_sales_dashboard.mgm_sales_dashboard'].search([]),
#         })

#     @http.route('/mgm_sales_dashboard/mgm_sales_dashboard/objects/<model("mgm_sales_dashboard.mgm_sales_dashboard"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgm_sales_dashboard.object', {
#             'object': obj
#         })