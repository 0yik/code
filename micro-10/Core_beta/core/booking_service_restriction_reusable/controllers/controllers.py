# -*- coding: utf-8 -*-
from odoo import http

# class Fields&flowReusable(http.Controller):
#     @http.route('/fields&flow_reusable/fields&flow_reusable/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fields&flow_reusable/fields&flow_reusable/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fields&flow_reusable.listing', {
#             'root': '/fields&flow_reusable/fields&flow_reusable',
#             'objects': http.request.env['fields&flow_reusable.fields&flow_reusable'].search([]),
#         })

#     @http.route('/fields&flow_reusable/fields&flow_reusable/objects/<model("fields&flow_reusable.fields&flow_reusable"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fields&flow_reusable.object', {
#             'object': obj
#         })