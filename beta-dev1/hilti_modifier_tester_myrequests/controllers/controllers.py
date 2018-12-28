# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class HiltiModifierTesterMyrequests(http.Controller):
    
    @http.route(['/my_requests'], type='http', auth="user", website=True)
    def my_requests(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_tester_myrequests', 'menu_action_my_request_view')[1]
        action_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_tester_myrequests', 'action_my_request_view')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))
    
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