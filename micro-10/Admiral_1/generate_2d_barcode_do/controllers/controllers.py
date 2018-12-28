# -*- coding: utf-8 -*-
from odoo import http

# class Generate2dBarcodeDo(http.Controller):
#     @http.route('/generate_2d_barcode_do/generate_2d_barcode_do/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/generate_2d_barcode_do/generate_2d_barcode_do/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('generate_2d_barcode_do.listing', {
#             'root': '/generate_2d_barcode_do/generate_2d_barcode_do',
#             'objects': http.request.env['generate_2d_barcode_do.generate_2d_barcode_do'].search([]),
#         })

#     @http.route('/generate_2d_barcode_do/generate_2d_barcode_do/objects/<model("generate_2d_barcode_do.generate_2d_barcode_do"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('generate_2d_barcode_do.object', {
#             'object': obj
#         })