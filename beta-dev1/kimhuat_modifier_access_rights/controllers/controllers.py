# -*- coding: utf-8 -*-
from odoo import http

# class KimhuatModifierAccessRights(http.Controller):
#     @http.route('/kimhuat_modifier_access_rights/kimhuat_modifier_access_rights/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kimhuat_modifier_access_rights/kimhuat_modifier_access_rights/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kimhuat_modifier_access_rights.listing', {
#             'root': '/kimhuat_modifier_access_rights/kimhuat_modifier_access_rights',
#             'objects': http.request.env['kimhuat_modifier_access_rights.kimhuat_modifier_access_rights'].search([]),
#         })

#     @http.route('/kimhuat_modifier_access_rights/kimhuat_modifier_access_rights/objects/<model("kimhuat_modifier_access_rights.kimhuat_modifier_access_rights"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kimhuat_modifier_access_rights.object', {
#             'object': obj
#         })