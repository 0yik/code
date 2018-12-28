# -*- coding: utf-8 -*-
from odoo import http

# class PosSarangOciHeader(http.Controller):
#     @http.route('/pos_sarang_oci_header/pos_sarang_oci_header/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_sarang_oci_header/pos_sarang_oci_header/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_sarang_oci_header.listing', {
#             'root': '/pos_sarang_oci_header/pos_sarang_oci_header',
#             'objects': http.request.env['pos_sarang_oci_header.pos_sarang_oci_header'].search([]),
#         })

#     @http.route('/pos_sarang_oci_header/pos_sarang_oci_header/objects/<model("pos_sarang_oci_header.pos_sarang_oci_header"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_sarang_oci_header.object', {
#             'object': obj
#         })