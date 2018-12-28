# -*- coding: utf-8 -*-
from odoo import http

# class MgmModiferTaxAdjustment(http.Controller):
#     @http.route('/mgm_modifer_tax_adjustment/mgm_modifer_tax_adjustment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgm_modifer_tax_adjustment/mgm_modifer_tax_adjustment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgm_modifer_tax_adjustment.listing', {
#             'root': '/mgm_modifer_tax_adjustment/mgm_modifer_tax_adjustment',
#             'objects': http.request.env['mgm_modifer_tax_adjustment.mgm_modifer_tax_adjustment'].search([]),
#         })

#     @http.route('/mgm_modifer_tax_adjustment/mgm_modifer_tax_adjustment/objects/<model("mgm_modifer_tax_adjustment.mgm_modifer_tax_adjustment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgm_modifer_tax_adjustment.object', {
#             'object': obj
#         })