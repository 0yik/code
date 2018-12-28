# -*- coding: utf-8 -*-
from odoo import http

# class PropellProject(http.Controller):
#     @http.route('/propell_project/propell_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/propell_project/propell_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('propell_project.listing', {
#             'root': '/propell_project/propell_project',
#             'objects': http.request.env['propell_project.propell_project'].search([]),
#         })

#     @http.route('/propell_project/propell_project/objects/<model("propell_project.propell_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('propell_project.object', {
#             'object': obj
#         })