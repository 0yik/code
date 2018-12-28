# -*- coding: utf-8 -*-
from odoo import http

# class LaborindoModifierInventoryValuation(http.Controller):
#     @http.route('/laborindo_modifier_inventory_valuation/laborindo_modifier_inventory_valuation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/laborindo_modifier_inventory_valuation/laborindo_modifier_inventory_valuation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('laborindo_modifier_inventory_valuation.listing', {
#             'root': '/laborindo_modifier_inventory_valuation/laborindo_modifier_inventory_valuation',
#             'objects': http.request.env['laborindo_modifier_inventory_valuation.laborindo_modifier_inventory_valuation'].search([]),
#         })

#     @http.route('/laborindo_modifier_inventory_valuation/laborindo_modifier_inventory_valuation/objects/<model("laborindo_modifier_inventory_valuation.laborindo_modifier_inventory_valuation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('laborindo_modifier_inventory_valuation.object', {
#             'object': obj
#         })