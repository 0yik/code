# -*- coding: utf-8 -*-
from odoo import http

# class BiocareModifierServicesMenu(http.Controller):
#     @http.route('/biocare_modifier_services_menu/biocare_modifier_services_menu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biocare_modifier_services_menu/biocare_modifier_services_menu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biocare_modifier_services_menu.listing', {
#             'root': '/biocare_modifier_services_menu/biocare_modifier_services_menu',
#             'objects': http.request.env['biocare_modifier_services_menu.biocare_modifier_services_menu'].search([]),
#         })

#     @http.route('/biocare_modifier_services_menu/biocare_modifier_services_menu/objects/<model("biocare_modifier_services_menu.biocare_modifier_services_menu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biocare_modifier_services_menu.object', {
#             'object': obj
#         })