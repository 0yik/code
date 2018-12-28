# -*- coding: utf-8 -*-
from odoo import http

# class 2dScanning(http.Controller):
#     @http.route('/2d_scanning/2d_scanning/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/2d_scanning/2d_scanning/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('2d_scanning.listing', {
#             'root': '/2d_scanning/2d_scanning',
#             'objects': http.request.env['2d_scanning.2d_scanning'].search([]),
#         })

#     @http.route('/2d_scanning/2d_scanning/objects/<model("2d_scanning.2d_scanning"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('2d_scanning.object', {
#             'object': obj
#         })