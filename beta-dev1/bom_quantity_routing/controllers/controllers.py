# -*- coding: utf-8 -*-
from odoo import http

# class BomQuantityRouting(http.Controller):
#     @http.route('/bom_quantity_routing/bom_quantity_routing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bom_quantity_routing/bom_quantity_routing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bom_quantity_routing.listing', {
#             'root': '/bom_quantity_routing/bom_quantity_routing',
#             'objects': http.request.env['bom_quantity_routing.bom_quantity_routing'].search([]),
#         })

#     @http.route('/bom_quantity_routing/bom_quantity_routing/objects/<model("bom_quantity_routing.bom_quantity_routing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bom_quantity_routing.object', {
#             'object': obj
#         })