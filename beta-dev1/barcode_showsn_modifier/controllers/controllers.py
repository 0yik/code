# -*- coding: utf-8 -*-
from odoo import http

# class BarcodeShowsnModifier(http.Controller):
#     @http.route('/barcode_showsn_modifier/barcode_showsn_modifier/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/barcode_showsn_modifier/barcode_showsn_modifier/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('barcode_showsn_modifier.listing', {
#             'root': '/barcode_showsn_modifier/barcode_showsn_modifier',
#             'objects': http.request.env['barcode_showsn_modifier.barcode_showsn_modifier'].search([]),
#         })

#     @http.route('/barcode_showsn_modifier/barcode_showsn_modifier/objects/<model("barcode_showsn_modifier.barcode_showsn_modifier"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('barcode_showsn_modifier.object', {
#             'object': obj
#         })