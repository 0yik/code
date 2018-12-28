# -*- coding: utf-8 -*-
from odoo import http

# class ManualBooking(http.Controller):
#     @http.route('/manual_booking/manual_booking/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/manual_booking/manual_booking/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('manual_booking.listing', {
#             'root': '/manual_booking/manual_booking',
#             'objects': http.request.env['manual_booking.manual_booking'].search([]),
#         })

#     @http.route('/manual_booking/manual_booking/objects/<model("manual_booking.manual_booking"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('manual_booking.object', {
#             'object': obj
#         })