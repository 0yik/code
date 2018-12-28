# -*- coding: utf-8 -*-
from odoo import http

# class PosSarangOciLayout(http.Controller):
#     @http.route('/pos_sarang_oci_layout/pos_sarang_oci_layout/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_sarang_oci_layout/pos_sarang_oci_layout/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_sarang_oci_layout.listing', {
#             'root': '/pos_sarang_oci_layout/pos_sarang_oci_layout',
#             'objects': http.request.env['pos_sarang_oci_layout.pos_sarang_oci_layout'].search([]),
#         })

#     @http.route('/pos_sarang_oci_layout/pos_sarang_oci_layout/objects/<model("pos_sarang_oci_layout.pos_sarang_oci_layout"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_sarang_oci_layout.object', {
#             'object': obj
#         })