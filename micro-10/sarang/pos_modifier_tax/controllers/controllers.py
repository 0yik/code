# -*- coding: utf-8 -*-
from odoo import http

# class PosModifierTax(http.Controller):
#     @http.route('/pos_modifier_tax/pos_modifier_tax/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_modifier_tax/pos_modifier_tax/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_modifier_tax.listing', {
#             'root': '/pos_modifier_tax/pos_modifier_tax',
#             'objects': http.request.env['pos_modifier_tax.pos_modifier_tax'].search([]),
#         })

#     @http.route('/pos_modifier_tax/pos_modifier_tax/objects/<model("pos_modifier_tax.pos_modifier_tax"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_modifier_tax.object', {
#             'object': obj
#         })