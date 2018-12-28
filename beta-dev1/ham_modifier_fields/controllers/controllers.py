# -*- coding: utf-8 -*-
from odoo import http

# class HamModifierFields(http.Controller):
#     @http.route('/ham_modifier_fields/ham_modifier_fields/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ham_modifier_fields/ham_modifier_fields/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ham_modifier_fields.listing', {
#             'root': '/ham_modifier_fields/ham_modifier_fields',
#             'objects': http.request.env['ham_modifier_fields.ham_modifier_fields'].search([]),
#         })

#     @http.route('/ham_modifier_fields/ham_modifier_fields/objects/<model("ham_modifier_fields.ham_modifier_fields"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ham_modifier_fields.object', {
#             'object': obj
#         })