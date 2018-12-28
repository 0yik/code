# -*- coding: utf-8 -*-
from odoo import http

# class AikchinModifierPartnerLedger(http.Controller):
#     @http.route('/aikchin_modifier_partner_ledger/aikchin_modifier_partner_ledger/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aikchin_modifier_partner_ledger/aikchin_modifier_partner_ledger/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aikchin_modifier_partner_ledger.listing', {
#             'root': '/aikchin_modifier_partner_ledger/aikchin_modifier_partner_ledger',
#             'objects': http.request.env['aikchin_modifier_partner_ledger.aikchin_modifier_partner_ledger'].search([]),
#         })

#     @http.route('/aikchin_modifier_partner_ledger/aikchin_modifier_partner_ledger/objects/<model("aikchin_modifier_partner_ledger.aikchin_modifier_partner_ledger"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aikchin_modifier_partner_ledger.object', {
#             'object': obj
#         })