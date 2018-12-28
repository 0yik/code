# -*- coding: utf-8 -*-
from odoo import http

# class HiltiModifierTesterMyrequests(http.Controller):
#     @http.route('/hilti_modifier_tester_myrequests/hilti_modifier_tester_myrequests/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hilti_modifier_tester_myrequests/hilti_modifier_tester_myrequests/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hilti_modifier_tester_myrequests.listing', {
#             'root': '/hilti_modifier_tester_myrequests/hilti_modifier_tester_myrequests',
#             'objects': http.request.env['hilti_modifier_tester_myrequests.hilti_modifier_tester_myrequests'].search([]),
#         })

#     @http.route('/hilti_modifier_tester_myrequests/hilti_modifier_tester_myrequests/objects/<model("hilti_modifier_tester_myrequests.hilti_modifier_tester_myrequests"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hilti_modifier_tester_myrequests.object', {
#             'object': obj
#         })