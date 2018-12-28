# -*- coding: utf-8 -*-
from odoo import http

# class LaborindoReportInvoiceSoc(http.Controller):
#     @http.route('/laborindo_report_invoice_soc/laborindo_report_invoice_soc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/laborindo_report_invoice_soc/laborindo_report_invoice_soc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('laborindo_report_invoice_soc.listing', {
#             'root': '/laborindo_report_invoice_soc/laborindo_report_invoice_soc',
#             'objects': http.request.env['laborindo_report_invoice_soc.laborindo_report_invoice_soc'].search([]),
#         })

#     @http.route('/laborindo_report_invoice_soc/laborindo_report_invoice_soc/objects/<model("laborindo_report_invoice_soc.laborindo_report_invoice_soc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('laborindo_report_invoice_soc.object', {
#             'object': obj
#         })