# -*- coding: utf-8 -*-
from odoo import http

# class TaxFreeButton(http.Controller):
#     @http.route('/tax_free_button/tax_free_button/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tax_free_button/tax_free_button/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tax_free_button.listing', {
#             'root': '/tax_free_button/tax_free_button',
#             'objects': http.request.env['tax_free_button.tax_free_button'].search([]),
#         })

#     @http.route('/tax_free_button/tax_free_button/objects/<model("tax_free_button.tax_free_button"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tax_free_button.object', {
#             'object': obj
#         })