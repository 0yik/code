# -*- coding: utf-8 -*-
from odoo import http

# class MultiDiscountPos(http.Controller):
#     @http.route('/multi_discount_pos/multi_discount_pos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/multi_discount_pos/multi_discount_pos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('multi_discount_pos.listing', {
#             'root': '/multi_discount_pos/multi_discount_pos',
#             'objects': http.request.env['multi_discount_pos.multi_discount_pos'].search([]),
#         })

#     @http.route('/multi_discount_pos/multi_discount_pos/objects/<model("multi_discount_pos.multi_discount_pos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('multi_discount_pos.object', {
#             'object': obj
#         })