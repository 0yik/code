# -*- coding: utf-8 -*-
from odoo import http

# class PdpInternalInvestmentStandard(http.Controller):
#     @http.route('/pdp_internal_investment_standard/pdp_internal_investment_standard/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pdp_internal_investment_standard/pdp_internal_investment_standard/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pdp_internal_investment_standard.listing', {
#             'root': '/pdp_internal_investment_standard/pdp_internal_investment_standard',
#             'objects': http.request.env['pdp_internal_investment_standard.pdp_internal_investment_standard'].search([]),
#         })

#     @http.route('/pdp_internal_investment_standard/pdp_internal_investment_standard/objects/<model("pdp_internal_investment_standard.pdp_internal_investment_standard"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pdp_internal_investment_standard.object', {
#             'object': obj
#         })