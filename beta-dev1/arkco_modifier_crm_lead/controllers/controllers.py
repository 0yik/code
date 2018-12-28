# -*- coding: utf-8 -*-
from odoo import http

# class ArkcoModifierCrmLead(http.Controller):
#     @http.route('/arkco_modifier_crm_lead/arkco_modifier_crm_lead/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/arkco_modifier_crm_lead/arkco_modifier_crm_lead/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('arkco_modifier_crm_lead.listing', {
#             'root': '/arkco_modifier_crm_lead/arkco_modifier_crm_lead',
#             'objects': http.request.env['arkco_modifier_crm_lead.arkco_modifier_crm_lead'].search([]),
#         })

#     @http.route('/arkco_modifier_crm_lead/arkco_modifier_crm_lead/objects/<model("arkco_modifier_crm_lead.arkco_modifier_crm_lead"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('arkco_modifier_crm_lead.object', {
#             'object': obj
#         })