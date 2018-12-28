# -*- coding: utf-8 -*-
from odoo import http

# class BudgetActualReport(http.Controller):
#     @http.route('/budget_actual_report/budget_actual_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/budget_actual_report/budget_actual_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('budget_actual_report.listing', {
#             'root': '/budget_actual_report/budget_actual_report',
#             'objects': http.request.env['budget_actual_report.budget_actual_report'].search([]),
#         })

#     @http.route('/budget_actual_report/budget_actual_report/objects/<model("budget_actual_report.budget_actual_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('budget_actual_report.object', {
#             'object': obj
#         })