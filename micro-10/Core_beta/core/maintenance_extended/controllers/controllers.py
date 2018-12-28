# -*- coding: utf-8 -*-
from odoo import http

# class MaintenanceExtended(http.Controller):
#     @http.route('/maintenance_extended/maintenance_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/maintenance_extended/maintenance_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('maintenance_extended.listing', {
#             'root': '/maintenance_extended/maintenance_extended',
#             'objects': http.request.env['maintenance_extended.maintenance_extended'].search([]),
#         })

#     @http.route('/maintenance_extended/maintenance_extended/objects/<model("maintenance_extended.maintenance_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('maintenance_extended.object', {
#             'object': obj
#         })