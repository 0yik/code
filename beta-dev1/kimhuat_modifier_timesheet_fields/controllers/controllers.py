# -*- coding: utf-8 -*-
from odoo import http

# class KimhuatModifierTimesheetFields(http.Controller):
#     @http.route('/kimhuat_modifier_timesheet_fields/kimhuat_modifier_timesheet_fields/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kimhuat_modifier_timesheet_fields/kimhuat_modifier_timesheet_fields/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kimhuat_modifier_timesheet_fields.listing', {
#             'root': '/kimhuat_modifier_timesheet_fields/kimhuat_modifier_timesheet_fields',
#             'objects': http.request.env['kimhuat_modifier_timesheet_fields.kimhuat_modifier_timesheet_fields'].search([]),
#         })

#     @http.route('/kimhuat_modifier_timesheet_fields/kimhuat_modifier_timesheet_fields/objects/<model("kimhuat_modifier_timesheet_fields.kimhuat_modifier_timesheet_fields"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kimhuat_modifier_timesheet_fields.object', {
#             'object': obj
#         })