# -*- coding: utf-8 -*-
from odoo import http

# class SalestargetAchievementIptCustom(http.Controller):
#     @http.route('/salestarget_achievement__ipt_custom/salestarget_achievement__ipt_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/salestarget_achievement__ipt_custom/salestarget_achievement__ipt_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('salestarget_achievement__ipt_custom.listing', {
#             'root': '/salestarget_achievement__ipt_custom/salestarget_achievement__ipt_custom',
#             'objects': http.request.env['salestarget_achievement__ipt_custom.salestarget_achievement__ipt_custom'].search([]),
#         })

#     @http.route('/salestarget_achievement__ipt_custom/salestarget_achievement__ipt_custom/objects/<model("salestarget_achievement__ipt_custom.salestarget_achievement__ipt_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('salestarget_achievement__ipt_custom.object', {
#             'object': obj
#         })