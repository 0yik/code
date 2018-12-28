# -*- coding: utf-8 -*-
from odoo import http

# class AikchinModifierPrintoutPayslips(http.Controller):
#     @http.route('/aikchin_modifier_printout_payslips/aikchin_modifier_printout_payslips/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aikchin_modifier_printout_payslips/aikchin_modifier_printout_payslips/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aikchin_modifier_printout_payslips.listing', {
#             'root': '/aikchin_modifier_printout_payslips/aikchin_modifier_printout_payslips',
#             'objects': http.request.env['aikchin_modifier_printout_payslips.aikchin_modifier_printout_payslips'].search([]),
#         })

#     @http.route('/aikchin_modifier_printout_payslips/aikchin_modifier_printout_payslips/objects/<model("aikchin_modifier_printout_payslips.aikchin_modifier_printout_payslips"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aikchin_modifier_printout_payslips.object', {
#             'object': obj
#         })