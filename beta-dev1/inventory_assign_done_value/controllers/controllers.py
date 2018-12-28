# -*- coding: utf-8 -*-
from odoo import http

# class InventoryAssignDoneValue(http.Controller):
#     @http.route('/inventory_assign_done_value/inventory_assign_done_value/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_assign_done_value/inventory_assign_done_value/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_assign_done_value.listing', {
#             'root': '/inventory_assign_done_value/inventory_assign_done_value',
#             'objects': http.request.env['inventory_assign_done_value.inventory_assign_done_value'].search([]),
#         })

#     @http.route('/inventory_assign_done_value/inventory_assign_done_value/objects/<model("inventory_assign_done_value.inventory_assign_done_value"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_assign_done_value.object', {
#             'object': obj
#         })