# -*- coding: utf-8 -*-
from odoo import http

# class AikchinModifierAnalyticAccounts(http.Controller):
#     @http.route('/aikchin_modifier_analytic_accounts/aikchin_modifier_analytic_accounts/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aikchin_modifier_analytic_accounts/aikchin_modifier_analytic_accounts/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aikchin_modifier_analytic_accounts.listing', {
#             'root': '/aikchin_modifier_analytic_accounts/aikchin_modifier_analytic_accounts',
#             'objects': http.request.env['aikchin_modifier_analytic_accounts.aikchin_modifier_analytic_accounts'].search([]),
#         })

#     @http.route('/aikchin_modifier_analytic_accounts/aikchin_modifier_analytic_accounts/objects/<model("aikchin_modifier_analytic_accounts.aikchin_modifier_analytic_accounts"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aikchin_modifier_analytic_accounts.object', {
#             'object': obj
#         })