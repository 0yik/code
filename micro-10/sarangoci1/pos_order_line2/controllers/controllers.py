# -*- coding: utf-8 -*-
from odoo import http

# class PosOrderLine(http.Controller):
#     @http.route('/pos_order_line/pos_order_line/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_order_line/pos_order_line/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_order_line.listing', {
#             'root': '/pos_order_line/pos_order_line',
#             'objects': http.request.env['pos_order_line.pos_order_line'].search([]),
#         })

#     @http.route('/pos_order_line/pos_order_line/objects/<model("pos_order_line.pos_order_line"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_order_line.object', {
#             'object': obj
#         })