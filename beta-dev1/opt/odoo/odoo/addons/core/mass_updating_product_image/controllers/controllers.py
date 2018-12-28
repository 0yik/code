# -*- coding: utf-8 -*-
from odoo import http

# class MassUpdatingProductImage(http.Controller):
#     @http.route('/mass_updating_product_image/mass_updating_product_image/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mass_updating_product_image/mass_updating_product_image/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mass_updating_product_image.listing', {
#             'root': '/mass_updating_product_image/mass_updating_product_image',
#             'objects': http.request.env['mass_updating_product_image.mass_updating_product_image'].search([]),
#         })

#     @http.route('/mass_updating_product_image/mass_updating_product_image/objects/<model("mass_updating_product_image.mass_updating_product_image"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mass_updating_product_image.object', {
#             'object': obj
#         })