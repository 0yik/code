# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseTenderFromContract(http.Controller):
#     @http.route('/purchase_tender_from_contract/purchase_tender_from_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_tender_from_contract/purchase_tender_from_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_tender_from_contract.listing', {
#             'root': '/purchase_tender_from_contract/purchase_tender_from_contract',
#             'objects': http.request.env['purchase_tender_from_contract.purchase_tender_from_contract'].search([]),
#         })

#     @http.route('/purchase_tender_from_contract/purchase_tender_from_contract/objects/<model("purchase_tender_from_contract.purchase_tender_from_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_tender_from_contract.object', {
#             'object': obj
#         })