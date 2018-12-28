# -*- coding: utf-8 -*-
from odoo import http

# class PosExitTableDiscardOrder(http.Controller):
#     @http.route('/pos_exit_table_discard_order/pos_exit_table_discard_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_exit_table_discard_order/pos_exit_table_discard_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_exit_table_discard_order.listing', {
#             'root': '/pos_exit_table_discard_order/pos_exit_table_discard_order',
#             'objects': http.request.env['pos_exit_table_discard_order.pos_exit_table_discard_order'].search([]),
#         })

#     @http.route('/pos_exit_table_discard_order/pos_exit_table_discard_order/objects/<model("pos_exit_table_discard_order.pos_exit_table_discard_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_exit_table_discard_order.object', {
#             'object': obj
#         })