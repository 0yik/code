# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseRequestModifierSarangoci(http.Controller):
#     @http.route('/purchase_request_modifier_sarangoci/purchase_request_modifier_sarangoci/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_request_modifier_sarangoci/purchase_request_modifier_sarangoci/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_request_modifier_sarangoci.listing', {
#             'root': '/purchase_request_modifier_sarangoci/purchase_request_modifier_sarangoci',
#             'objects': http.request.env['purchase_request_modifier_sarangoci.purchase_request_modifier_sarangoci'].search([]),
#         })

#     @http.route('/purchase_request_modifier_sarangoci/purchase_request_modifier_sarangoci/objects/<model("purchase_request_modifier_sarangoci.purchase_request_modifier_sarangoci"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_request_modifier_sarangoci.object', {
#             'object': obj
#         })