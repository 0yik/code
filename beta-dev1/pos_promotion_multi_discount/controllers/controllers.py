# -*- coding: utf-8 -*-
from odoo import http

# class PosPromotionMultiDiscount(http.Controller):
#     @http.route('/pos_promotion_multi_discount/pos_promotion_multi_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_promotion_multi_discount/pos_promotion_multi_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_promotion_multi_discount.listing', {
#             'root': '/pos_promotion_multi_discount/pos_promotion_multi_discount',
#             'objects': http.request.env['pos_promotion_multi_discount.pos_promotion_multi_discount'].search([]),
#         })

#     @http.route('/pos_promotion_multi_discount/pos_promotion_multi_discount/objects/<model("pos_promotion_multi_discount.pos_promotion_multi_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_promotion_multi_discount.object', {
#             'object': obj
#         })