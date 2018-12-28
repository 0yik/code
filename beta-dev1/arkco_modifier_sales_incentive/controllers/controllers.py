# -*- coding: utf-8 -*-
from odoo import http

# class ArkcoModifierSalesIncentive(http.Controller):
#     @http.route('/arkco_modifier_sales_incentive/arkco_modifier_sales_incentive/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/arkco_modifier_sales_incentive/arkco_modifier_sales_incentive/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('arkco_modifier_sales_incentive.listing', {
#             'root': '/arkco_modifier_sales_incentive/arkco_modifier_sales_incentive',
#             'objects': http.request.env['arkco_modifier_sales_incentive.arkco_modifier_sales_incentive'].search([]),
#         })

#     @http.route('/arkco_modifier_sales_incentive/arkco_modifier_sales_incentive/objects/<model("arkco_modifier_sales_incentive.arkco_modifier_sales_incentive"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('arkco_modifier_sales_incentive.object', {
#             'object': obj
#         })