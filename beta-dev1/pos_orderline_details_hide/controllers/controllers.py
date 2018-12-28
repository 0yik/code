# -*- coding: utf-8 -*-
from odoo import http

# class PosOrderlineDetailsHide(http.Controller):
#     @http.route('/pos_orderline_details_hide/pos_orderline_details_hide/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_orderline_details_hide/pos_orderline_details_hide/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_orderline_details_hide.listing', {
#             'root': '/pos_orderline_details_hide/pos_orderline_details_hide',
#             'objects': http.request.env['pos_orderline_details_hide.pos_orderline_details_hide'].search([]),
#         })

#     @http.route('/pos_orderline_details_hide/pos_orderline_details_hide/objects/<model("pos_orderline_details_hide.pos_orderline_details_hide"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_orderline_details_hide.object', {
#             'object': obj
#         })