# -*- coding: utf-8 -*-
from odoo import http

# class AdmiralModifierInventoryCheckBom(http.Controller):
#     @http.route('/admiral_modifier_inventory_check_bom/admiral_modifier_inventory_check_bom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/admiral_modifier_inventory_check_bom/admiral_modifier_inventory_check_bom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('admiral_modifier_inventory_check_bom.listing', {
#             'root': '/admiral_modifier_inventory_check_bom/admiral_modifier_inventory_check_bom',
#             'objects': http.request.env['admiral_modifier_inventory_check_bom.admiral_modifier_inventory_check_bom'].search([]),
#         })

#     @http.route('/admiral_modifier_inventory_check_bom/admiral_modifier_inventory_check_bom/objects/<model("admiral_modifier_inventory_check_bom.admiral_modifier_inventory_check_bom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('admiral_modifier_inventory_check_bom.object', {
#             'object': obj
#         })