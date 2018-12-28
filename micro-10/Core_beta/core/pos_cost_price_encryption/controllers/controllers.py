# -*- coding: utf-8 -*-
from odoo import http

# class PosCostPriceEncryption(http.Controller):
#     @http.route('/pos_cost_price_encryption/pos_cost_price_encryption/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_cost_price_encryption/pos_cost_price_encryption/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_cost_price_encryption.listing', {
#             'root': '/pos_cost_price_encryption/pos_cost_price_encryption',
#             'objects': http.request.env['pos_cost_price_encryption.pos_cost_price_encryption'].search([]),
#         })

#     @http.route('/pos_cost_price_encryption/pos_cost_price_encryption/objects/<model("pos_cost_price_encryption.pos_cost_price_encryption"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_cost_price_encryption.object', {
#             'object': obj
#         })