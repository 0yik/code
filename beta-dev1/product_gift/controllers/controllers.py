# -*- coding: utf-8 -*-
from odoo import http

# class AikchinProductBundle(http.Controller):
#     @http.route('/aikchin_product_bundle/aikchin_product_bundle/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aikchin_product_bundle/aikchin_product_bundle/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aikchin_product_bundle.listing', {
#             'root': '/aikchin_product_bundle/aikchin_product_bundle',
#             'objects': http.request.env['aikchin_product_bundle.aikchin_product_bundle'].search([]),
#         })

#     @http.route('/aikchin_product_bundle/aikchin_product_bundle/objects/<model("aikchin_product_bundle.aikchin_product_bundle"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aikchin_product_bundle.object', {
#             'object': obj
#         })