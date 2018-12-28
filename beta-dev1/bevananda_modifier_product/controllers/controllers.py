# -*- coding: utf-8 -*-
from odoo import http

# class BevanandaModifierProduct(http.Controller):
#     @http.route('/bevananda_modifier_product/bevananda_modifier_product/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bevananda_modifier_product/bevananda_modifier_product/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bevananda_modifier_product.listing', {
#             'root': '/bevananda_modifier_product/bevananda_modifier_product',
#             'objects': http.request.env['bevananda_modifier_product.bevananda_modifier_product'].search([]),
#         })

#     @http.route('/bevananda_modifier_product/bevananda_modifier_product/objects/<model("bevananda_modifier_product.bevananda_modifier_product"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bevananda_modifier_product.object', {
#             'object': obj
#         })