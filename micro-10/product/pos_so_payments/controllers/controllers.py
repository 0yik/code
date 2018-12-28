# -*- coding: utf-8 -*-
from odoo import http

# class PosSoPayments(http.Controller):
#     @http.route('/pos_so_payments/pos_so_payments/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_so_payments/pos_so_payments/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_so_payments.listing', {
#             'root': '/pos_so_payments/pos_so_payments',
#             'objects': http.request.env['pos_so_payments.pos_so_payments'].search([]),
#         })

#     @http.route('/pos_so_payments/pos_so_payments/objects/<model("pos_so_payments.pos_so_payments"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_so_payments.object', {
#             'object': obj
#         })