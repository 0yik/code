# -*- coding: utf-8 -*-
from odoo import http

# class LeaveOffInLieu(http.Controller):
#     @http.route('/leave_off_in_lieu/leave_off_in_lieu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/leave_off_in_lieu/leave_off_in_lieu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('leave_off_in_lieu.listing', {
#             'root': '/leave_off_in_lieu/leave_off_in_lieu',
#             'objects': http.request.env['leave_off_in_lieu.leave_off_in_lieu'].search([]),
#         })

#     @http.route('/leave_off_in_lieu/leave_off_in_lieu/objects/<model("leave_off_in_lieu.leave_off_in_lieu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('leave_off_in_lieu.object', {
#             'object': obj
#         })