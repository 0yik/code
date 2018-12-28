# -*- coding: utf-8 -*-
from odoo import http

# class PdpModifierBranch(http.Controller):
#     @http.route('/pdp_modifier_branch/pdp_modifier_branch/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pdp_modifier_branch/pdp_modifier_branch/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pdp_modifier_branch.listing', {
#             'root': '/pdp_modifier_branch/pdp_modifier_branch',
#             'objects': http.request.env['pdp_modifier_branch.pdp_modifier_branch'].search([]),
#         })

#     @http.route('/pdp_modifier_branch/pdp_modifier_branch/objects/<model("pdp_modifier_branch.pdp_modifier_branch"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pdp_modifier_branch.object', {
#             'object': obj
#         })