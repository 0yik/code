# -*- coding: utf-8 -*-
from odoo import http

# class WasteManagement(http.Controller):
#     @http.route('/waste_management/waste_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/waste_management/waste_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('waste_management.listing', {
#             'root': '/waste_management/waste_management',
#             'objects': http.request.env['waste_management.waste_management'].search([]),
#         })

#     @http.route('/waste_management/waste_management/objects/<model("waste_management.waste_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('waste_management.object', {
#             'object': obj
#         })