# -*- coding: utf-8 -*-
from odoo import http

# class PosUserAccess(http.Controller):
#     @http.route('/pos_user_access/pos_user_access/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_user_access/pos_user_access/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_user_access.listing', {
#             'root': '/pos_user_access/pos_user_access',
#             'objects': http.request.env['pos_user_access.pos_user_access'].search([]),
#         })

#     @http.route('/pos_user_access/pos_user_access/objects/<model("pos_user_access.pos_user_access"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_user_access.object', {
#             'object': obj
#         })