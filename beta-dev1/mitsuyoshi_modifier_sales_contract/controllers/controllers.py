# -*- coding: utf-8 -*-
from odoo import http

# class MitsuyoshiModifierSalesContract(http.Controller):
#     @http.route('/mitsuyoshi_modifier_sales_contract/mitsuyoshi_modifier_sales_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mitsuyoshi_modifier_sales_contract/mitsuyoshi_modifier_sales_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mitsuyoshi_modifier_sales_contract.listing', {
#             'root': '/mitsuyoshi_modifier_sales_contract/mitsuyoshi_modifier_sales_contract',
#             'objects': http.request.env['mitsuyoshi_modifier_sales_contract.mitsuyoshi_modifier_sales_contract'].search([]),
#         })

#     @http.route('/mitsuyoshi_modifier_sales_contract/mitsuyoshi_modifier_sales_contract/objects/<model("mitsuyoshi_modifier_sales_contract.mitsuyoshi_modifier_sales_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mitsuyoshi_modifier_sales_contract.object', {
#             'object': obj
#         })