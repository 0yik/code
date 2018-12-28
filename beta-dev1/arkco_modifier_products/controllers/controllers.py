# -*- coding: utf-8 -*-
from odoo import http

# class ArkcoModifierProducts(http.Controller):
#     @http.route('/arkco_modifier_products/arkco_modifier_products/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/arkco_modifier_products/arkco_modifier_products/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('arkco_modifier_products.listing', {
#             'root': '/arkco_modifier_products/arkco_modifier_products',
#             'objects': http.request.env['arkco_modifier_products.arkco_modifier_products'].search([]),
#         })

#     @http.route('/arkco_modifier_products/arkco_modifier_products/objects/<model("arkco_modifier_products.arkco_modifier_products"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('arkco_modifier_products.object', {
#             'object': obj
#         })