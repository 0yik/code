# -*- coding: utf-8 -*-
from odoo import http

# class PricelistItemMenuReusable(http.Controller):
#     @http.route('/pricelist_item_menu_reusable/pricelist_item_menu_reusable/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pricelist_item_menu_reusable/pricelist_item_menu_reusable/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pricelist_item_menu_reusable.listing', {
#             'root': '/pricelist_item_menu_reusable/pricelist_item_menu_reusable',
#             'objects': http.request.env['pricelist_item_menu_reusable.pricelist_item_menu_reusable'].search([]),
#         })

#     @http.route('/pricelist_item_menu_reusable/pricelist_item_menu_reusable/objects/<model("pricelist_item_menu_reusable.pricelist_item_menu_reusable"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pricelist_item_menu_reusable.object', {
#             'object': obj
#         })