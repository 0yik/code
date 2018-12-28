# -*- coding: utf-8 -*-
from odoo import http

# class ContractFromSoJobestimate(http.Controller):
#     @http.route('/contract_from_so_jobestimate/contract_from_so_jobestimate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_from_so_jobestimate/contract_from_so_jobestimate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_from_so_jobestimate.listing', {
#             'root': '/contract_from_so_jobestimate/contract_from_so_jobestimate',
#             'objects': http.request.env['contract_from_so_jobestimate.contract_from_so_jobestimate'].search([]),
#         })

#     @http.route('/contract_from_so_jobestimate/contract_from_so_jobestimate/objects/<model("contract_from_so_jobestimate.contract_from_so_jobestimate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_from_so_jobestimate.object', {
#             'object': obj
#         })