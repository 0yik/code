# -*- coding: utf-8 -*-
from odoo import http

# class CustomerModifier(http.Controller):
#     @http.route('/customer_modifier/customer_modifier/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_modifier/customer_modifier/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_modifier.listing', {
#             'root': '/customer_modifier/customer_modifier',
#             'objects': http.request.env['customer_modifier.customer_modifier'].search([]),
#         })

#     @http.route('/customer_modifier/customer_modifier/objects/<model("customer_modifier.customer_modifier"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_modifier.object', {
#             'object': obj
#         })