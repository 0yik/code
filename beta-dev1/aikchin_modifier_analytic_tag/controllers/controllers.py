# -*- coding: utf-8 -*-
from odoo import http

# class AikchinModifierAnalyticTag(http.Controller):
#     @http.route('/aikchin_modifier_analytic_tag/aikchin_modifier_analytic_tag/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aikchin_modifier_analytic_tag/aikchin_modifier_analytic_tag/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aikchin_modifier_analytic_tag.listing', {
#             'root': '/aikchin_modifier_analytic_tag/aikchin_modifier_analytic_tag',
#             'objects': http.request.env['aikchin_modifier_analytic_tag.aikchin_modifier_analytic_tag'].search([]),
#         })

#     @http.route('/aikchin_modifier_analytic_tag/aikchin_modifier_analytic_tag/objects/<model("aikchin_modifier_analytic_tag.aikchin_modifier_analytic_tag"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aikchin_modifier_analytic_tag.object', {
#             'object': obj
#         })