# -*- coding: utf-8 -*-
from odoo import http

# class BranchSalesReport(http.Controller):
#     @http.route('/branch_sales_report/branch_sales_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/branch_sales_report/branch_sales_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('branch_sales_report.listing', {
#             'root': '/branch_sales_report/branch_sales_report',
#             'objects': http.request.env['branch_sales_report.branch_sales_report'].search([]),
#         })

#     @http.route('/branch_sales_report/branch_sales_report/objects/<model("branch_sales_report.branch_sales_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('branch_sales_report.object', {
#             'object': obj
#         })