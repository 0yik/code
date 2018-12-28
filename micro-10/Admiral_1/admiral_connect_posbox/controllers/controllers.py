# -*- coding: utf-8 -*-
from odoo import http

# class AdmiralConnectPosbox(http.Controller):
#     @http.route('/admiral_connect_posbox/admiral_connect_posbox/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/admiral_connect_posbox/admiral_connect_posbox/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('admiral_connect_posbox.listing', {
#             'root': '/admiral_connect_posbox/admiral_connect_posbox',
#             'objects': http.request.env['admiral_connect_posbox.admiral_connect_posbox'].search([]),
#         })

#     @http.route('/admiral_connect_posbox/admiral_connect_posbox/objects/<model("admiral_connect_posbox.admiral_connect_posbox"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('admiral_connect_posbox.object', {
#             'object': obj
#         })