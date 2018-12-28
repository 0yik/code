# -*- coding: utf-8 -*-
from odoo import http

# class PosDiscountTotalHm(http.Controller):
#     @http.route('/pos_discount_total_hm/pos_discount_total_hm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_discount_total_hm/pos_discount_total_hm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_discount_total_hm.listing', {
#             'root': '/pos_discount_total_hm/pos_discount_total_hm',
#             'objects': http.request.env['pos_discount_total_hm.pos_discount_total_hm'].search([]),
#         })

#     @http.route('/pos_discount_total_hm/pos_discount_total_hm/objects/<model("pos_discount_total_hm.pos_discount_total_hm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_discount_total_hm.object', {
#             'object': obj
#         })