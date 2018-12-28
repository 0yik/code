# -*- coding: utf-8 -*-
from odoo import http

# class DzhRevisionCallLogModify(http.Controller):
#     @http.route('/dzh_revision_call_log_modify/dzh_revision_call_log_modify/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dzh_revision_call_log_modify/dzh_revision_call_log_modify/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dzh_revision_call_log_modify.listing', {
#             'root': '/dzh_revision_call_log_modify/dzh_revision_call_log_modify',
#             'objects': http.request.env['dzh_revision_call_log_modify.dzh_revision_call_log_modify'].search([]),
#         })

#     @http.route('/dzh_revision_call_log_modify/dzh_revision_call_log_modify/objects/<model("dzh_revision_call_log_modify.dzh_revision_call_log_modify"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dzh_revision_call_log_modify.object', {
#             'object': obj
#         })