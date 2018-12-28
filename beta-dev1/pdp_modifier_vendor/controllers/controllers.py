# -*- coding: utf-8 -*-
from odoo import http

# class PdpModifierVendor(http.Controller):
#     @http.route('/pdp_modifier_vendor/pdp_modifier_vendor/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pdp_modifier_vendor/pdp_modifier_vendor/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pdp_modifier_vendor.listing', {
#             'root': '/pdp_modifier_vendor/pdp_modifier_vendor',
#             'objects': http.request.env['pdp_modifier_vendor.pdp_modifier_vendor'].search([]),
#         })

#     @http.route('/pdp_modifier_vendor/pdp_modifier_vendor/objects/<model("pdp_modifier_vendor.pdp_modifier_vendor"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pdp_modifier_vendor.object', {
#             'object': obj
#         })