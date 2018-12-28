# -*- coding: utf-8 -*-
from odoo import http

# class HiltiModifierCompanyCustomization(http.Controller):
#     @http.route('/hilti_modifier_company_customization/hilti_modifier_company_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hilti_modifier_company_customization/hilti_modifier_company_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hilti_modifier_company_customization.listing', {
#             'root': '/hilti_modifier_company_customization/hilti_modifier_company_customization',
#             'objects': http.request.env['hilti_modifier_company_customization.hilti_modifier_company_customization'].search([]),
#         })

#     @http.route('/hilti_modifier_company_customization/hilti_modifier_company_customization/objects/<model("hilti_modifier_company_customization.hilti_modifier_company_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hilti_modifier_company_customization.object', {
#             'object': obj
#         })