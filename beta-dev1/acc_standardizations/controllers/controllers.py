# -*- coding: utf-8 -*-
from odoo import http

# class AccStandardizations(http.Controller):
#     @http.route('/acc_standardizations/acc_standardizations/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/acc_standardizations/acc_standardizations/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('acc_standardizations.listing', {
#             'root': '/acc_standardizations/acc_standardizations',
#             'objects': http.request.env['acc_standardizations.acc_standardizations'].search([]),
#         })

#     @http.route('/acc_standardizations/acc_standardizations/objects/<model("acc_standardizations.acc_standardizations"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('acc_standardizations.object', {
#             'object': obj
#         })