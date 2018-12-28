# -*- coding: utf-8 -*-
from odoo import http

# class LaborindoModifierInvoiceNumber(http.Controller):
#     @http.route('/laborindo_modifier_invoice_number/laborindo_modifier_invoice_number/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/laborindo_modifier_invoice_number/laborindo_modifier_invoice_number/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('laborindo_modifier_invoice_number.listing', {
#             'root': '/laborindo_modifier_invoice_number/laborindo_modifier_invoice_number',
#             'objects': http.request.env['laborindo_modifier_invoice_number.laborindo_modifier_invoice_number'].search([]),
#         })

#     @http.route('/laborindo_modifier_invoice_number/laborindo_modifier_invoice_number/objects/<model("laborindo_modifier_invoice_number.laborindo_modifier_invoice_number"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('laborindo_modifier_invoice_number.object', {
#             'object': obj
#         })