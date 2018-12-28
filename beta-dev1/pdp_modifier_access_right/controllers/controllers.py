# -*- coding: utf-8 -*-
from odoo import http

# class PdpModifierAccessRight(http.Controller):
#     @http.route('/pdp_modifier_access_right/pdp_modifier_access_right/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pdp_modifier_access_right/pdp_modifier_access_right/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pdp_modifier_access_right.listing', {
#             'root': '/pdp_modifier_access_right/pdp_modifier_access_right',
#             'objects': http.request.env['pdp_modifier_access_right.pdp_modifier_access_right'].search([]),
#         })

#     @http.route('/pdp_modifier_access_right/pdp_modifier_access_right/objects/<model("pdp_modifier_access_right.pdp_modifier_access_right"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pdp_modifier_access_right.object', {
#             'object': obj
#         })