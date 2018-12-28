# -*- coding: utf-8 -*-
from odoo import http

# class AikchinModifierAppraisalRatings(http.Controller):
#     @http.route('/aikchin_modifier_appraisal_ratings/aikchin_modifier_appraisal_ratings/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aikchin_modifier_appraisal_ratings/aikchin_modifier_appraisal_ratings/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aikchin_modifier_appraisal_ratings.listing', {
#             'root': '/aikchin_modifier_appraisal_ratings/aikchin_modifier_appraisal_ratings',
#             'objects': http.request.env['aikchin_modifier_appraisal_ratings.aikchin_modifier_appraisal_ratings'].search([]),
#         })

#     @http.route('/aikchin_modifier_appraisal_ratings/aikchin_modifier_appraisal_ratings/objects/<model("aikchin_modifier_appraisal_ratings.aikchin_modifier_appraisal_ratings"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aikchin_modifier_appraisal_ratings.object', {
#             'object': obj
#         })