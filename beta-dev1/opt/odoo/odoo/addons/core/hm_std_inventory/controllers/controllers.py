# -*- coding: utf-8 -*-
from odoo import http

# class HmStdInventory(http.Controller):
#     @http.route('/hm_std_inventory/hm_std_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hm_std_inventory/hm_std_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hm_std_inventory.listing', {
#             'root': '/hm_std_inventory/hm_std_inventory',
#             'objects': http.request.env['hm_std_inventory.hm_std_inventory'].search([]),
#         })

#     @http.route('/hm_std_inventory/hm_std_inventory/objects/<model("hm_std_inventory.hm_std_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hm_std_inventory.object', {
#             'object': obj
#         })