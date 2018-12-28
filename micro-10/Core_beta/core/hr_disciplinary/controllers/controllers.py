# -*- coding: utf-8 -*-
from odoo import http

# class HrDisciplinary(http.Controller):
#     @http.route('/hr_disciplinary/hr_disciplinary/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_disciplinary/hr_disciplinary/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_disciplinary.listing', {
#             'root': '/hr_disciplinary/hr_disciplinary',
#             'objects': http.request.env['hr_disciplinary.hr_disciplinary'].search([]),
#         })

#     @http.route('/hr_disciplinary/hr_disciplinary/objects/<model("hr_disciplinary.hr_disciplinary"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_disciplinary.object', {
#             'object': obj
#         })