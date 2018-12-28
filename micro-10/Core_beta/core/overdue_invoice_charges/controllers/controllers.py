# -*- coding: utf-8 -*-
from odoo import http

# class OverdueInvoiceCharges(http.Controller):
#     @http.route('/overdue_invoice_charges/overdue_invoice_charges/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/overdue_invoice_charges/overdue_invoice_charges/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('overdue_invoice_charges.listing', {
#             'root': '/overdue_invoice_charges/overdue_invoice_charges',
#             'objects': http.request.env['overdue_invoice_charges.overdue_invoice_charges'].search([]),
#         })

#     @http.route('/overdue_invoice_charges/overdue_invoice_charges/objects/<model("overdue_invoice_charges.overdue_invoice_charges"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('overdue_invoice_charges.object', {
#             'object': obj
#         })