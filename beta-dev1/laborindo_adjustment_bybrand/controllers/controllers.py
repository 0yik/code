# -*- coding: utf-8 -*-
from odoo import http

# class LaborindoAdjustmentBybrand(http.Controller):
#     @http.route('/laborindo_adjustment_bybrand/laborindo_adjustment_bybrand/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/laborindo_adjustment_bybrand/laborindo_adjustment_bybrand/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('laborindo_adjustment_bybrand.listing', {
#             'root': '/laborindo_adjustment_bybrand/laborindo_adjustment_bybrand',
#             'objects': http.request.env['laborindo_adjustment_bybrand.laborindo_adjustment_bybrand'].search([]),
#         })

#     @http.route('/laborindo_adjustment_bybrand/laborindo_adjustment_bybrand/objects/<model("laborindo_adjustment_bybrand.laborindo_adjustment_bybrand"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('laborindo_adjustment_bybrand.object', {
#             'object': obj
#         })