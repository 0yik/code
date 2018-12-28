# -*- coding: utf-8 -*-
from odoo import http

# class PosPromotionReport(http.Controller):
#     @http.route('/pos_promotion_report/pos_promotion_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_promotion_report/pos_promotion_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_promotion_report.listing', {
#             'root': '/pos_promotion_report/pos_promotion_report',
#             'objects': http.request.env['pos_promotion_report.pos_promotion_report'].search([]),
#         })

#     @http.route('/pos_promotion_report/pos_promotion_report/objects/<model("pos_promotion_report.pos_promotion_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_promotion_report.object', {
#             'object': obj
#         })