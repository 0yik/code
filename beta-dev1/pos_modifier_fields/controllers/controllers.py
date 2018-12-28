# -*- coding: utf-8 -*-
from odoo import http

# class PosModifierFields(http.Controller):
#     @http.route('/pos_modifier_fields/pos_modifier_fields/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_modifier_fields/pos_modifier_fields/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_modifier_fields.listing', {
#             'root': '/pos_modifier_fields/pos_modifier_fields',
#             'objects': http.request.env['pos_modifier_fields.pos_modifier_fields'].search([]),
#         })

#     @http.route('/pos_modifier_fields/pos_modifier_fields/objects/<model("pos_modifier_fields.pos_modifier_fields"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_modifier_fields.object', {
#             'object': obj
#         })