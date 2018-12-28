# -*- coding: utf-8 -*-
from odoo import http

# class PosReceiptLogo(http.Controller):
#     @http.route('/pos_receipt_logo/pos_receipt_logo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_receipt_logo/pos_receipt_logo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_receipt_logo.listing', {
#             'root': '/pos_receipt_logo/pos_receipt_logo',
#             'objects': http.request.env['pos_receipt_logo.pos_receipt_logo'].search([]),
#         })

#     @http.route('/pos_receipt_logo/pos_receipt_logo/objects/<model("pos_receipt_logo.pos_receipt_logo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_receipt_logo.object', {
#             'object': obj
#         })