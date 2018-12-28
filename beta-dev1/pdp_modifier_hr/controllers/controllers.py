# -*- coding: utf-8 -*-
from odoo import http

# class PdpModifierHr(http.Controller):
#     @http.route('/pdp_modifier__hr/pdp_modifier__hr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pdp_modifier__hr/pdp_modifier__hr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pdp_modifier__hr.listing', {
#             'root': '/pdp_modifier__hr/pdp_modifier__hr',
#             'objects': http.request.env['pdp_modifier__hr.pdp_modifier__hr'].search([]),
#         })

#     @http.route('/pdp_modifier__hr/pdp_modifier__hr/objects/<model("pdp_modifier__hr.pdp_modifier__hr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pdp_modifier__hr.object', {
#             'object': obj
#         })