# -*- coding: utf-8 -*-
from odoo import http

# class HideStockMenus(http.Controller):
#     @http.route('/hide_stock_menus/hide_stock_menus/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hide_stock_menus/hide_stock_menus/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hide_stock_menus.listing', {
#             'root': '/hide_stock_menus/hide_stock_menus',
#             'objects': http.request.env['hide_stock_menus.hide_stock_menus'].search([]),
#         })

#     @http.route('/hide_stock_menus/hide_stock_menus/objects/<model("hide_stock_menus.hide_stock_menus"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hide_stock_menus.object', {
#             'object': obj
#         })