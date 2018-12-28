# -*- coding: utf-8 -*-
from odoo import http

# class MultiDiscountPricelist(http.Controller):
#     @http.route('/multi_discount_pricelist/multi_discount_pricelist/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/multi_discount_pricelist/multi_discount_pricelist/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('multi_discount_pricelist.listing', {
#             'root': '/multi_discount_pricelist/multi_discount_pricelist',
#             'objects': http.request.env['multi_discount_pricelist.multi_discount_pricelist'].search([]),
#         })

#     @http.route('/multi_discount_pricelist/multi_discount_pricelist/objects/<model("multi_discount_pricelist.multi_discount_pricelist"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('multi_discount_pricelist.object', {
#             'object': obj
#         })