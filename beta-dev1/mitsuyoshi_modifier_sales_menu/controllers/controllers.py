# -*- coding: utf-8 -*-
from odoo import http

# class MitsuyoshiModifierSalesMenu(http.Controller):
#     @http.route('/mitsuyoshi_modifier_sales_menu/mitsuyoshi_modifier_sales_menu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mitsuyoshi_modifier_sales_menu/mitsuyoshi_modifier_sales_menu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mitsuyoshi_modifier_sales_menu.listing', {
#             'root': '/mitsuyoshi_modifier_sales_menu/mitsuyoshi_modifier_sales_menu',
#             'objects': http.request.env['mitsuyoshi_modifier_sales_menu.mitsuyoshi_modifier_sales_menu'].search([]),
#         })

#     @http.route('/mitsuyoshi_modifier_sales_menu/mitsuyoshi_modifier_sales_menu/objects/<model("mitsuyoshi_modifier_sales_menu.mitsuyoshi_modifier_sales_menu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mitsuyoshi_modifier_sales_menu.object', {
#             'object': obj
#         })