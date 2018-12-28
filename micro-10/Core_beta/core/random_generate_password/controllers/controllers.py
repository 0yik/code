# -*- coding: utf-8 -*-
from odoo import http

# class RandomGeneratePassword(http.Controller):
#     @http.route('/random_generate_password/random_generate_password/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/random_generate_password/random_generate_password/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('random_generate_password.listing', {
#             'root': '/random_generate_password/random_generate_password',
#             'objects': http.request.env['random_generate_password.random_generate_password'].search([]),
#         })

#     @http.route('/random_generate_password/random_generate_password/objects/<model("random_generate_password.random_generate_password"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('random_generate_password.object', {
#             'object': obj
#         })