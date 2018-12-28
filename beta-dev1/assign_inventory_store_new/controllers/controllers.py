# -*- coding: utf-8 -*-
from odoo import http

# class AssignInventoryStoreNew(http.Controller):
#     @http.route('/assign_inventory_store_new/assign_inventory_store_new/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/assign_inventory_store_new/assign_inventory_store_new/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('assign_inventory_store_new.listing', {
#             'root': '/assign_inventory_store_new/assign_inventory_store_new',
#             'objects': http.request.env['assign_inventory_store_new.assign_inventory_store_new'].search([]),
#         })

#     @http.route('/assign_inventory_store_new/assign_inventory_store_new/objects/<model("assign_inventory_store_new.assign_inventory_store_new"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('assign_inventory_store_new.object', {
#             'object': obj
#         })