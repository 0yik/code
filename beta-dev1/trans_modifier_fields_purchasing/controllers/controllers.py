# -*- coding: utf-8 -*-
from odoo import http

# class TransModifierFieldsPurchasing(http.Controller):
#     @http.route('/trans_modifier_fields_purchasing/trans_modifier_fields_purchasing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/trans_modifier_fields_purchasing/trans_modifier_fields_purchasing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('trans_modifier_fields_purchasing.listing', {
#             'root': '/trans_modifier_fields_purchasing/trans_modifier_fields_purchasing',
#             'objects': http.request.env['trans_modifier_fields_purchasing.trans_modifier_fields_purchasing'].search([]),
#         })

#     @http.route('/trans_modifier_fields_purchasing/trans_modifier_fields_purchasing/objects/<model("trans_modifier_fields_purchasing.trans_modifier_fields_purchasing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('trans_modifier_fields_purchasing.object', {
#             'object': obj
#         })