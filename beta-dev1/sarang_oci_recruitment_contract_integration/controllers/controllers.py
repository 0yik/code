# -*- coding: utf-8 -*-
from odoo import http

# class SarangOciRecruitmentContractIntegration(http.Controller):
#     @http.route('/sarang_oci_recruitment_contract_integration/sarang_oci_recruitment_contract_integration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sarang_oci_recruitment_contract_integration/sarang_oci_recruitment_contract_integration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sarang_oci_recruitment_contract_integration.listing', {
#             'root': '/sarang_oci_recruitment_contract_integration/sarang_oci_recruitment_contract_integration',
#             'objects': http.request.env['sarang_oci_recruitment_contract_integration.sarang_oci_recruitment_contract_integration'].search([]),
#         })

#     @http.route('/sarang_oci_recruitment_contract_integration/sarang_oci_recruitment_contract_integration/objects/<model("sarang_oci_recruitment_contract_integration.sarang_oci_recruitment_contract_integration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sarang_oci_recruitment_contract_integration.object', {
#             'object': obj
#         })