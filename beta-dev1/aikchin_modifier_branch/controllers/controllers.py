# -*- coding: utf-8 -*-
from odoo import http

# class AikchinModifierBranch(http.Controller):
#     @http.route('/aikchin_modifier_branch/aikchin_modifier_branch/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aikchin_modifier_branch/aikchin_modifier_branch/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aikchin_modifier_branch.listing', {
#             'root': '/aikchin_modifier_branch/aikchin_modifier_branch',
#             'objects': http.request.env['aikchin_modifier_branch.aikchin_modifier_branch'].search([]),
#         })

#     @http.route('/aikchin_modifier_branch/aikchin_modifier_branch/objects/<model("aikchin_modifier_branch.aikchin_modifier_branch"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aikchin_modifier_branch.object', {
#             'object': obj
#         })