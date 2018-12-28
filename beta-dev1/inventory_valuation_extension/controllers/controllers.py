# -*- coding: utf-8 -*-
from odoo import http

# class InventoryValuationExtension(http.Controller):
#     @http.route('/inventory_valuation_extension/inventory_valuation_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_valuation_extension/inventory_valuation_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_valuation_extension.listing', {
#             'root': '/inventory_valuation_extension/inventory_valuation_extension',
#             'objects': http.request.env['inventory_valuation_extension.inventory_valuation_extension'].search([]),
#         })

#     @http.route('/inventory_valuation_extension/inventory_valuation_extension/objects/<model("inventory_valuation_extension.inventory_valuation_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_valuation_extension.object', {
#             'object': obj
#         })