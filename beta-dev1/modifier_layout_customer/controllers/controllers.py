# -*- coding: utf-8 -*-
from odoo import http

# class MatahariModifierFieldCustomer(http.Controller):
#     @http.route('/matahari_modifier_field_customer/matahari_modifier_field_customer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/matahari_modifier_field_customer/matahari_modifier_field_customer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('matahari_modifier_field_customer.listing', {
#             'root': '/matahari_modifier_field_customer/matahari_modifier_field_customer',
#             'objects': http.request.env['matahari_modifier_field_customer.matahari_modifier_field_customer'].search([]),
#         })

#     @http.route('/matahari_modifier_field_customer/matahari_modifier_field_customer/objects/<model("matahari_modifier_field_customer.matahari_modifier_field_customer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('matahari_modifier_field_customer.object', {
#             'object': obj
#         })