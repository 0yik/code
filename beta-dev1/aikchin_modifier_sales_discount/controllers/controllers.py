# -*- coding: utf-8 -*-
from odoo import http

# class AikchinModifierSalesDiscount(http.Controller):
#     @http.route('/aikchin_modifier_sales_discount/aikchin_modifier_sales_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aikchin_modifier_sales_discount/aikchin_modifier_sales_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aikchin_modifier_sales_discount.listing', {
#             'root': '/aikchin_modifier_sales_discount/aikchin_modifier_sales_discount',
#             'objects': http.request.env['aikchin_modifier_sales_discount.aikchin_modifier_sales_discount'].search([]),
#         })

#     @http.route('/aikchin_modifier_sales_discount/aikchin_modifier_sales_discount/objects/<model("aikchin_modifier_sales_discount.aikchin_modifier_sales_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aikchin_modifier_sales_discount.object', {
#             'object': obj
#         })