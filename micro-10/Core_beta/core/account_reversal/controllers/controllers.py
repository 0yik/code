# -*- coding: utf-8 -*-
from odoo import http

# class AccountReversal(http.Controller):
#     @http.route('/account_reversal/account_reversal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_reversal/account_reversal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_reversal.listing', {
#             'root': '/account_reversal/account_reversal',
#             'objects': http.request.env['account_reversal.account_reversal'].search([]),
#         })

#     @http.route('/account_reversal/account_reversal/objects/<model("account_reversal.account_reversal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_reversal.object', {
#             'object': obj
#         })