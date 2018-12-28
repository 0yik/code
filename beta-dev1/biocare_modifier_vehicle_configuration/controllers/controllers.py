# -*- coding: utf-8 -*-
from odoo import http

# class BiocareModifierVehicleConfiguration(http.Controller):
#     @http.route('/biocare_modifier_vehicle_configuration/biocare_modifier_vehicle_configuration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biocare_modifier_vehicle_configuration/biocare_modifier_vehicle_configuration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biocare_modifier_vehicle_configuration.listing', {
#             'root': '/biocare_modifier_vehicle_configuration/biocare_modifier_vehicle_configuration',
#             'objects': http.request.env['biocare_modifier_vehicle_configuration.biocare_modifier_vehicle_configuration'].search([]),
#         })

#     @http.route('/biocare_modifier_vehicle_configuration/biocare_modifier_vehicle_configuration/objects/<model("biocare_modifier_vehicle_configuration.biocare_modifier_vehicle_configuration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biocare_modifier_vehicle_configuration.object', {
#             'object': obj
#         })