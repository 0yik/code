# -*- coding: utf-8 -*-
from odoo import http

# class PosPrintSessionRevenue(http.Controller):
#     @http.route('/pos_print_session_revenue/pos_print_session_revenue/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_print_session_revenue/pos_print_session_revenue/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_print_session_revenue.listing', {
#             'root': '/pos_print_session_revenue/pos_print_session_revenue',
#             'objects': http.request.env['pos_print_session_revenue.pos_print_session_revenue'].search([]),
#         })

#     @http.route('/pos_print_session_revenue/pos_print_session_revenue/objects/<model("pos_print_session_revenue.pos_print_session_revenue"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_print_session_revenue.object', {
#             'object': obj
#         })