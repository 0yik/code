# -*- coding: utf-8 -*-
from odoo import http

# class KimhuatModifierFields(http.Controller):
#     @http.route('/kimhuat_modifier_fields/kimhuat_modifier_fields/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kimhuat_modifier_fields/kimhuat_modifier_fields/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kimhuat_modifier_fields.listing', {
#             'root': '/kimhuat_modifier_fields/kimhuat_modifier_fields',
#             'objects': http.request.env['kimhuat_modifier_fields.kimhuat_modifier_fields'].search([]),
#         })

#     @http.route('/kimhuat_modifier_fields/kimhuat_modifier_fields/objects/<model("kimhuat_modifier_fields.kimhuat_modifier_fields"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kimhuat_modifier_fields.object', {
#             'object': obj
#         })