# -*- coding: utf-8 -*-
from odoo import http

# class MgmModiferAccessRight(http.Controller):
#     @http.route('/mgm_modifer_access_right/mgm_modifer_access_right/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgm_modifer_access_right/mgm_modifer_access_right/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgm_modifer_access_right.listing', {
#             'root': '/mgm_modifer_access_right/mgm_modifer_access_right',
#             'objects': http.request.env['mgm_modifer_access_right.mgm_modifer_access_right'].search([]),
#         })

#     @http.route('/mgm_modifer_access_right/mgm_modifer_access_right/objects/<model("mgm_modifer_access_right.mgm_modifer_access_right"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgm_modifer_access_right.object', {
#             'object': obj
#         })