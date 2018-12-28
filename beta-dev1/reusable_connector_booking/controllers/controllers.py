# -*- coding: utf-8 -*-
from odoo import http

# class ReusableConnectorBooking(http.Controller):
#     @http.route('/reusable_connector_booking/reusable_connector_booking/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reusable_connector_booking/reusable_connector_booking/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reusable_connector_booking.listing', {
#             'root': '/reusable_connector_booking/reusable_connector_booking',
#             'objects': http.request.env['reusable_connector_booking.reusable_connector_booking'].search([]),
#         })

#     @http.route('/reusable_connector_booking/reusable_connector_booking/objects/<model("reusable_connector_booking.reusable_connector_booking"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reusable_connector_booking.object', {
#             'object': obj
#         })