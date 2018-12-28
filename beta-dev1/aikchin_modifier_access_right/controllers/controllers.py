# -*- coding: utf-8 -*-
from odoo import http

# class AikchinModifierAccessRight(http.Controller):
#     @http.route('/aikchin_modifier_access_right/aikchin_modifier_access_right/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aikchin_modifier_access_right/aikchin_modifier_access_right/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aikchin_modifier_access_right.listing', {
#             'root': '/aikchin_modifier_access_right/aikchin_modifier_access_right',
#             'objects': http.request.env['aikchin_modifier_access_right.aikchin_modifier_access_right'].search([]),
#         })

#     @http.route('/aikchin_modifier_access_right/aikchin_modifier_access_right/objects/<model("aikchin_modifier_access_right.aikchin_modifier_access_right"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aikchin_modifier_access_right.object', {
#             'object': obj
#         })