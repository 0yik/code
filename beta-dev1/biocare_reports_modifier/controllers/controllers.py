# -*- coding: utf-8 -*-
from odoo import http

# class BiocareReportsModifier(http.Controller):
#     @http.route('/biocare_reports_modifier/biocare_reports_modifier/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biocare_reports_modifier/biocare_reports_modifier/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biocare_reports_modifier.listing', {
#             'root': '/biocare_reports_modifier/biocare_reports_modifier',
#             'objects': http.request.env['biocare_reports_modifier.biocare_reports_modifier'].search([]),
#         })

#     @http.route('/biocare_reports_modifier/biocare_reports_modifier/objects/<model("biocare_reports_modifier.biocare_reports_modifier"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biocare_reports_modifier.object', {
#             'object': obj
#         })