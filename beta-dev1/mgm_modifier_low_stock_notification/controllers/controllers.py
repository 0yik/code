# -*- coding: utf-8 -*-
from odoo import http

# class MgmModifierLowStockNotification(http.Controller):
#     @http.route('/mgm_modifier_low_stock_notification/mgm_modifier_low_stock_notification/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgm_modifier_low_stock_notification/mgm_modifier_low_stock_notification/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgm_modifier_low_stock_notification.listing', {
#             'root': '/mgm_modifier_low_stock_notification/mgm_modifier_low_stock_notification',
#             'objects': http.request.env['mgm_modifier_low_stock_notification.mgm_modifier_low_stock_notification'].search([]),
#         })

#     @http.route('/mgm_modifier_low_stock_notification/mgm_modifier_low_stock_notification/objects/<model("mgm_modifier_low_stock_notification.mgm_modifier_low_stock_notification"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgm_modifier_low_stock_notification.object', {
#             'object': obj
#         })