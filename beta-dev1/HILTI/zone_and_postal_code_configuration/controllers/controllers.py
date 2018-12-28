# -*- coding: utf-8 -*-
from odoo import http

# class ZoneAndPostalCodeConfiguration(http.Controller):
#     @http.route('/zone_and_postal_code_configuration/zone_and_postal_code_configuration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zone_and_postal_code_configuration/zone_and_postal_code_configuration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zone_and_postal_code_configuration.listing', {
#             'root': '/zone_and_postal_code_configuration/zone_and_postal_code_configuration',
#             'objects': http.request.env['zone_and_postal_code_configuration.zone_and_postal_code_configuration'].search([]),
#         })

#     @http.route('/zone_and_postal_code_configuration/zone_and_postal_code_configuration/objects/<model("zone_and_postal_code_configuration.zone_and_postal_code_configuration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zone_and_postal_code_configuration.object', {
#             'object': obj
#         })