# -*- coding: utf-8 -*-
from odoo import http

# class BevanandaModifierForecastedCost(http.Controller):
#     @http.route('/bevananda_modifier_forecasted_cost/bevananda_modifier_forecasted_cost/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bevananda_modifier_forecasted_cost/bevananda_modifier_forecasted_cost/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bevananda_modifier_forecasted_cost.listing', {
#             'root': '/bevananda_modifier_forecasted_cost/bevananda_modifier_forecasted_cost',
#             'objects': http.request.env['bevananda_modifier_forecasted_cost.bevananda_modifier_forecasted_cost'].search([]),
#         })

#     @http.route('/bevananda_modifier_forecasted_cost/bevananda_modifier_forecasted_cost/objects/<model("bevananda_modifier_forecasted_cost.bevananda_modifier_forecasted_cost"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bevananda_modifier_forecasted_cost.object', {
#             'object': obj
#         })