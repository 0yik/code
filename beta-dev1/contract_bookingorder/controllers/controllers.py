# -*- coding: utf-8 -*-
from odoo import http

# class BiocareContractModifier(http.Controller):
#     @http.route('/biocare_contract_modifier/biocare_contract_modifier/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biocare_contract_modifier/biocare_contract_modifier/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biocare_contract_modifier.listing', {
#             'root': '/biocare_contract_modifier/biocare_contract_modifier',
#             'objects': http.request.env['biocare_contract_modifier.biocare_contract_modifier'].search([]),
#         })

#     @http.route('/biocare_contract_modifier/biocare_contract_modifier/objects/<model("biocare_contract_modifier.biocare_contract_modifier"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biocare_contract_modifier.object', {
#             'object': obj
#         })