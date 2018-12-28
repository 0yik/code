# -*- coding: utf-8 -*-
from odoo import http

# class WarehouseSerializerMrp(http.Controller):
#     @http.route('/warehouse_serializer_mrp/warehouse_serializer_mrp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/warehouse_serializer_mrp/warehouse_serializer_mrp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('warehouse_serializer_mrp.listing', {
#             'root': '/warehouse_serializer_mrp/warehouse_serializer_mrp',
#             'objects': http.request.env['warehouse_serializer_mrp.warehouse_serializer_mrp'].search([]),
#         })

#     @http.route('/warehouse_serializer_mrp/warehouse_serializer_mrp/objects/<model("warehouse_serializer_mrp.warehouse_serializer_mrp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('warehouse_serializer_mrp.object', {
#             'object': obj
#         })